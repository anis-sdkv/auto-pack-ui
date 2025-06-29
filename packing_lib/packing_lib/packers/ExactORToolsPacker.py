from typing import List

from ortools.sat.python import cp_model

from packing_lib.packing_lib.interfaces.BasePacker import BasePacker
from packing_lib.packing_lib.types import PlacedObject, PackingInputTask, PackInputObject, PackingContainer


class ExactORToolsPacker(BasePacker):
    def __init__(self, time_limit_seconds: int = 300, allow_rotation: bool = True,
                 try_subsets: bool = True):

        self.time_limit_seconds = time_limit_seconds
        self.allow_rotation = allow_rotation
        self.try_subsets = try_subsets

    def pack(self, task: PackingInputTask) -> List[PlacedObject]:
        import itertools

        n = len(task.objects)

        for size in range(n, 0, -1):
            max_attempts = 20 if size > 8 else 100
            attempts = 0

            for subset in itertools.combinations(task.objects, size):
                if attempts >= max_attempts:
                    break

                attempts += 1
                result = self._try_pack(task, list(subset))

                if result:
                    print(f"Упаковано {size} из {n} объектов")
                    return result

        print("Решение не найдено")
        return []

    def _try_pack(self, task: PackingInputTask, objects: List[PackInputObject]) -> List[PlacedObject]:
        if not objects:
            return []

        container_width = int(task.container.width - 2 * task.container.padding)
        container_height = int(task.container.height - 2 * task.container.padding)

        rectangles = self._prepare_rectangles(objects)

        model = cp_model.CpModel()

        variables = self._create_variables(model, rectangles, container_width, container_height)

        self._add_constraints(model, variables, rectangles, container_width, container_height)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit_seconds
        solver.parameters.log_search_progress = False

        status = solver.Solve(model)

        if status == cp_model.OPTIMAL:
            return self._extract_solution(solver, variables, rectangles, task.container)
        elif status == cp_model.FEASIBLE:
            return self._extract_solution(solver, variables, rectangles, task.container)
        else:
            return []

    def _prepare_rectangles(self, objects: List[PackInputObject]) -> List[dict]:
        rectangles = []

        for obj in objects:
            rect_data = {
                'id': obj.id,
                'width': int(obj.width),
                'height': int(obj.height),
                'rotatable': self.allow_rotation and obj.width != obj.height
            }
            rectangles.append(rect_data)

        return rectangles

    def _create_variables(self, model, rectangles, container_width, container_height):
        variables = {}

        for i, rect in enumerate(rectangles):
            variables[f'x_{i}'] = model.NewIntVar(0, container_width - rect['width'], f'x_{i}')
            variables[f'y_{i}'] = model.NewIntVar(0, container_height - rect['height'], f'y_{i}')

            if rect['rotatable']:
                variables[f'rotated_{i}'] = model.NewBoolVar(f'rotated_{i}')
                variables[f'actual_width_{i}'] = model.NewIntVar(
                    min(rect['width'], rect['height']),
                    max(rect['width'], rect['height']),
                    f'actual_width_{i}'
                )
                variables[f'actual_height_{i}'] = model.NewIntVar(
                    min(rect['width'], rect['height']),
                    max(rect['width'], rect['height']),
                    f'actual_height_{i}'
                )
            else:
                variables[f'rotated_{i}'] = None
                variables[f'actual_width_{i}'] = rect['width']
                variables[f'actual_height_{i}'] = rect['height']

        return variables

    def _add_constraints(self, model, variables, rectangles, container_width, container_height):
        n = len(rectangles)

        for i, rect in enumerate(rectangles):
            if rect['rotatable']:
                model.Add(variables[f'actual_width_{i}'] == rect['width']).OnlyEnforceIf(
                    variables[f'rotated_{i}'].Not())
                model.Add(variables[f'actual_height_{i}'] == rect['height']).OnlyEnforceIf(
                    variables[f'rotated_{i}'].Not())

                model.Add(variables[f'actual_width_{i}'] == rect['height']).OnlyEnforceIf(
                    variables[f'rotated_{i}'])
                model.Add(variables[f'actual_height_{i}'] == rect['width']).OnlyEnforceIf(
                    variables[f'rotated_{i}'])

        for i, rect in enumerate(rectangles):
            if rect['rotatable']:
                model.Add(variables[f'x_{i}'] + variables[f'actual_width_{i}'] <= container_width)
                model.Add(variables[f'y_{i}'] + variables[f'actual_height_{i}'] <= container_height)
            else:
                model.Add(variables[f'x_{i}'] + rect['width'] <= container_width)
                model.Add(variables[f'y_{i}'] + rect['height'] <= container_height)

        for i in range(n):
            for j in range(i + 1, n):
                self._add_non_overlap_constraint(model, variables, i, j, rectangles)

    def _add_non_overlap_constraint(self, model, variables, i, j, rectangles):
        left = model.NewBoolVar(f'left_{i}_{j}')
        if rectangles[i]['rotatable']:
            model.Add(variables[f'x_{i}'] + variables[f'actual_width_{i}'] <= variables[f'x_{j}']).OnlyEnforceIf(left)
        else:
            model.Add(variables[f'x_{i}'] + rectangles[i]['width'] <= variables[f'x_{j}']).OnlyEnforceIf(left)

        right = model.NewBoolVar(f'right_{i}_{j}')
        if rectangles[j]['rotatable']:
            model.Add(variables[f'x_{j}'] + variables[f'actual_width_{j}'] <= variables[f'x_{i}']).OnlyEnforceIf(right)
        else:
            model.Add(variables[f'x_{j}'] + rectangles[j]['width'] <= variables[f'x_{i}']).OnlyEnforceIf(right)

        below = model.NewBoolVar(f'below_{i}_{j}')
        if rectangles[i]['rotatable']:
            model.Add(variables[f'y_{i}'] + variables[f'actual_height_{i}'] <= variables[f'y_{j}']).OnlyEnforceIf(below)
        else:
            model.Add(variables[f'y_{i}'] + rectangles[i]['height'] <= variables[f'y_{j}']).OnlyEnforceIf(below)

        above = model.NewBoolVar(f'above_{i}_{j}')
        if rectangles[j]['rotatable']:
            model.Add(variables[f'y_{j}'] + variables[f'actual_height_{j}'] <= variables[f'y_{i}']).OnlyEnforceIf(above)
        else:
            model.Add(variables[f'y_{j}'] + rectangles[j]['height'] <= variables[f'y_{i}']).OnlyEnforceIf(above)

        model.AddBoolOr([left, right, below, above])

    def _extract_solution(self, solver, variables, rectangles, container: PackingContainer) -> List[PlacedObject]:
        placed_objects = []

        for i, rect in enumerate(rectangles):
            x = solver.Value(variables[f'x_{i}'])
            y = solver.Value(variables[f'y_{i}'])

            if rect['rotatable']:
                width = solver.Value(variables[f'actual_width_{i}'])
                height = solver.Value(variables[f'actual_height_{i}'])
            else:
                width = rect['width']
                height = rect['height']

            left_x = container.padding + x
            top_y = container.padding + y
            center_x = left_x + width / 2
            center_y = top_y + height / 2

            placed_objects.append(PlacedObject(
                id=rect['id'],
                center_x=center_x,
                center_y=center_y,
                width=width,
                height=height
            ))

        return placed_objects

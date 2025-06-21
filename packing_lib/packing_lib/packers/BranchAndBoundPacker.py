from typing import List
from packing_lib.packing_lib.interfaces.BasePacker import BasePacker
from packing_lib.packing_lib.types import PackingTask, PlacedObject, RectObject


class BranchAndBoundPacker(BasePacker):
    def pack(self, task: PackingTask) -> List[PlacedObject]:
        best_solution: List[PlacedObject] = []
        container_w = task.container.width
        container_h = task.container.height
        total_objects = len(task.objects)
        attempts = 0
        updates = 0

        def is_valid_placement(x: float, y: float, w: float, h: float, placed: List[PlacedObject]) -> bool:
            if x + w > container_w or y + h > container_h:
                return False
            for p in placed:
                if not (x + w <= p.x or x >= p.x + p.width or
                        y + h <= p.y or y >= p.y + p.height):
                    return False
            return True

        def branch(remaining: List[RectObject], placed: List[PlacedObject]):
            nonlocal best_solution, attempts, updates
            attempts += 1

            if len(placed) > len(best_solution):
                best_solution = placed.copy()
                updates += 1
                print(f"[Update #{updates}] New best with {len(best_solution)} placed out of {total_objects}.")

            if not remaining:
                return

            obj = remaining[0]
            rest = remaining[1:]
            step = 5.0

            for x in range(0, int(container_w - obj.width + 1), int(step)):
                for y in range(0, int(container_h - obj.height + 1), int(step)):
                    if is_valid_placement(x, y, obj.width, obj.height, placed):
                        placed.append(PlacedObject(id=obj.id, x=x, y=y, width=obj.width, height=obj.height))
                        branch(rest, placed)
                        placed.pop()

            branch(rest, placed)

        sorted_objects = sorted(task.objects, key=lambda o: o.width * o.height, reverse=True)
        print(f"[Start] Branch and Bound started with {len(sorted_objects)} objects.")
        branch(sorted_objects, [])
        print(f"[Finish] Done after {attempts} attempts. Best packed: {len(best_solution)} objects.")
        return best_solution

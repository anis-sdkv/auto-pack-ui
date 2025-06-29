import json
import math
from typing import List, Tuple, Dict, Optional

from packing_lib.packing_lib.types import (
    RectObject, PlacedObject,
    InputInstruction, OutputInstruction, ManipulatorInstruction
)


class ManipulatorInstructionGenerator:
    """Генератор инструкций для манипулятора на основе детекции и результатов упаковки"""

    def __init__(
            self,
            container_world_position: Tuple[float, float],
            manipulator_origin_offset: Optional[Tuple[float, float]] = None,
            precision: int = 2
    ):
        """
        Args:
            container_world_position: координаты левой верхней точки контейнера в реальном мире (x, y)
            manipulator_origin_offset: смещение начала координат системы манипулятора
                                     относительно базовой системы координат (dx, dy).
                                     Все координаты будут пересчитаны: new_coord = old_coord + offset.
                                     По умолчанию (0, 0) - без смещения.
            precision: количество знаков после запятой для округления. По умолчанию 2
        """
        self.container_position = container_world_position
        self.manipulator_origin_offset = manipulator_origin_offset or (0.0, 0.0)
        self.precision = precision
        self.default_drop_height = 0.0  # заглушка для z координаты

    def _round_value(self, value: float) -> float:
        """Округляет значение до заданной точности и конвертирует NumPy типы в Python native"""
        # Конвертируем NumPy типы в Python native float для JSON сериализации
        return round(float(value), self.precision)

    def _apply_manipulator_offset(self, x: float, y: float) -> Tuple[float, float]:
        """
        Применяет смещение начала координат системы манипулятора

        Преобразует координаты из базовой системы в систему координат манипулятора:
        manipulator_x = base_x + offset_x
        manipulator_y = base_y + offset_y
        """
        return (
            x + self.manipulator_origin_offset[0],
            y + self.manipulator_origin_offset[1]
        )

    def generate_instructions(
            self,
            detected_objects: List[RectObject],
            packed_objects: List[PlacedObject]
    ) -> Tuple[List[ManipulatorInstruction], List[int]]:
        """
        Генерирует инструкции для манипулятора

        Args:
            detected_objects: объекты с результатами детекции
            packed_objects: результаты упаковки

        Returns:
            Кортеж: (список инструкций для манипулятора, список ID неупакованных объектов)
        """
        # Создаем словарь для быстрого поиска объектов по ID
        detected_dict = {obj.id: obj for obj in detected_objects}
        packed_dict = {obj.id: obj for obj in packed_objects}

        instructions = []

        # Обрабатываем только объекты, которые есть и в детекции, и в упаковке
        common_ids = set(detected_dict.keys()) & set(packed_dict.keys())

        for obj_id in sorted(common_ids):
            detected = detected_dict[obj_id]
            packed = packed_dict[obj_id]

            # Применяем смещение начала координат манипулятора к входным координатам
            input_x, input_y = self._apply_manipulator_offset(detected.center_mm[0], detected.center_mm[1])

            # Формируем входную инструкцию (параметры захвата)
            input_instr = InputInstruction(
                x=self._round_value(input_x),
                y=self._round_value(input_y),
                z=self._round_value(detected.z),
                theta=self._round_value(detected.angle_deg),
                w=self._round_value(detected.width),
                h=self._round_value(detected.height)
            )

            # Вычисляем угол поворота для размещения
            rotation_angle = self._calculate_rotation_angle(detected, packed)

            # Вычисляем размеры после поворота
            rotated_w, rotated_h = self._get_rotated_dimensions(
                detected.width, detected.height, rotation_angle
            )

            # Применяем смещение начала координат манипулятора к выходным координатам
            # packed теперь содержит center_x, center_y
            output_x = self.container_position[0] + packed.center_x
            output_y = self.container_position[1] + packed.center_y
            output_x, output_y = self._apply_manipulator_offset(output_x, output_y)

            # Формируем выходную инструкцию (параметры размещения)
            # Размеры остаются такими же, как в input - изменяется только угол
            output_instr = OutputInstruction(
                x=self._round_value(output_x),
                y=self._round_value(output_y),
                z=self._round_value(self.default_drop_height),
                theta=self._round_value(rotation_angle),
                w=self._round_value(detected.width),
                h=self._round_value(detected.height)
            )

            instructions.append(ManipulatorInstruction(
                id=obj_id,
                input=input_instr,
                output=output_instr
            ))

        # Находим ID неупакованных объектов
        unpacked_ids = list(set(detected_dict.keys()) - set(packed_dict.keys()))
        
        return instructions, unpacked_ids

    def _calculate_rotation_angle(self, detected: RectObject, packed: PlacedObject) -> float:
        """
        Вычисляет угол поворота объекта при размещении

        Логика:
        1. Проверяем, был ли объект повернут при упаковке (сравниваем соотношения сторон)
        2. Если повернут → поворот на 90° относительно исходного
        3. Если не повернут → минимальный поворот к ортогональному углу
        """
        # Определяем, был ли объект повернут при упаковке
        original_aspect = detected.width / detected.height
        packed_aspect = packed.width / packed.height

        # Порог для определения поворота (учитываем возможные погрешности)
        aspect_threshold = 0.1

        was_rotated = abs(original_aspect - 1 / packed_aspect) < abs(original_aspect - packed_aspect)

        if was_rotated:
            # Объект был повернут на 90° при упаковке
            target_angle = detected.angle_deg + 90
        else:
            # Объект не был повернут, используем исходную ориентацию
            target_angle = detected.angle_deg

        # Нормализуем к ближайшему ортогональному углу
        return self._normalize_to_orthogonal(target_angle)

    def _normalize_to_orthogonal(self, angle: float) -> float:
        """Приводит угол к ближайшему ортогональному значению (0°, 90°, 180°, 270°)"""
        # Нормализуем угол к диапазону [0, 360)
        angle = angle % 360

        orthogonal_angles = [0, 90, 180, 270]

        # Находим ближайший ортогональный угол
        distances = [min(abs(angle - orth), abs(angle - orth + 360), abs(angle - orth - 360))
                     for orth in orthogonal_angles]

        closest_index = distances.index(min(distances))
        return orthogonal_angles[closest_index]

    def _get_rotated_dimensions(self, width: float, height: float, angle: float) -> Tuple[float, float]:
        """Возвращает размеры объекта после поворота на заданный угол"""
        # Нормализуем угол
        angle = angle % 360

        # Для ортогональных углов
        if angle in [90, 270]:
            return height, width  # Поворот на 90° или 270° - меняем местами
        else:
            return width, height  # 0° или 180° - размеры не меняются

    def save_to_json(self, instructions: List[ManipulatorInstruction], unpacked_ids: List[int], filepath: str) -> None:
        """
        Сохраняет инструкции в JSON файл

        Args:
            instructions: список инструкций
            unpacked_ids: список ID неупакованных объектов
            filepath: путь для сохранения файла
        """
        # Преобразуем в словарь для JSON сериализации
        data = {
            "manipulator_instructions": [
                {
                    "id": instr.id,
                    "input": {
                        "x": instr.input.x,
                        "y": instr.input.y,
                        "z": instr.input.z,
                        "theta": instr.input.theta,
                        "w": instr.input.w,
                        "h": instr.input.h
                    },
                    "output": {
                        "x": instr.output.x,
                        "y": instr.output.y,
                        "z": instr.output.z,
                        "theta": instr.output.theta,
                        "w": instr.output.w,
                        "h": instr.output.h
                    }
                }
                for instr in instructions
            ],
            "metadata": {
                "container_position": [
                    self._round_value(pos) for pos in self.container_position
                ],
                "manipulator_origin_offset": [
                    self._round_value(offset) for offset in self.manipulator_origin_offset
                ],
                "precision": self.precision,
                "total_objects": len(instructions),
                "drop_height": self._round_value(self.default_drop_height),
                "unpacked_object_ids": sorted(unpacked_ids),
                "unpacked_count": len(unpacked_ids)
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_from_json(filepath: str) -> List[ManipulatorInstruction]:
        """
        Загружает инструкции из JSON файла

        Args:
            filepath: путь к файлу

        Returns:
            Список инструкций для манипулятора
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        instructions = []
        for item in data["manipulator_instructions"]:
            input_instr = InputInstruction(**item["input"])
            output_instr = OutputInstruction(**item["output"])

            instructions.append(ManipulatorInstruction(
                id=item["id"],
                input=input_instr,
                output=output_instr
            ))

        return instructions
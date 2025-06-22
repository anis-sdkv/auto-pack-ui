from typing import List
import random

import cv2
import numpy as np
from app.AppConfig import AppConfig
from packing_lib.packing_lib.SceneProcessor import SceneProcessor
from packing_lib.packing_lib.detectors.ArucoDetector import ArucoBoxDetector
from packing_lib.packing_lib.detectors.YoloBoxDetector import YoloBoxDetector
from packing_lib.packing_lib.packers.ExactORToolsPacker import ExactORToolsPacker
from packing_lib.packing_lib.packers.NFDHPacker import NFDHPacker
from packing_lib.packing_lib.packers.PhysPacker import PhysPacker
from packing_lib.packing_lib.types import SceneProcessResult, PackingInputTask, PackInput, PackingContainer
from packing_lib.packing_lib.visualization.PlacedObjectsVisualizer import PlacedObjectsVisualizer
from packing_lib.packing_lib.manipulation.ManipulatorInstructionGenerator import ManipulatorInstructionGenerator
from packing_lib.packing_lib.visualization.SceneProcessVisualizer import SceneProcessVisualizer


def generate_random_objects(count: int, min_size: float = 1.0, max_size: float = 4.0) -> List[PackInput]:
    """Генерирует случайный набор объектов для упаковки"""
    objects = []
    for i in range(count):
        width = random.uniform(min_size, max_size)
        height = random.uniform(min_size, max_size)
        objects.append(PackInput(id=i, width=width, height=height))
    return objects


if __name__ == "__main__":
    container = PackingContainer(19, 11)
    input_dir = "../../in/"
    output_dir = "../../out/"

    # Генерируем случайный набор данных для тестирования
    random_objects = generate_random_objects(count=50, min_size=1, max_size=4)

    # Используем случайные данные
    task = PackingInputTask(container, random_objects)

    # Или можно использовать данные детекции:
    # frame = cv2.imread(input_dir + "det7.jpg")
    # aruco = ArucoBoxDetector(2.3, AppConfig.camera_matrix, AppConfig.dist_coeffs)
    # yolo = YoloBoxDetector()
    # processor = SceneProcessor(aruco, yolo)
    # result = processor.process(frame)
    # task = PackingInputTask(
    #     container,
    #     PackingInputTask.from_rect_objects(result.converted_objects)
    # )

    # Используем масштабирование для лучшей визуализации
    # Можно попробовать разные режимы:
    # packer = PhysPacker(headless=True)  # максимальная скорость
    # packer = PhysPacker(headless=False, simulation_speed=10.0)  # ускоренная визуализация
    packer = PhysPacker(headless=False, pixels_per_mm=40, simulation_speed=2.0)
    # packer = ExactORToolsPacker()
    placed_objects = packer.pack(task)

    # Визуализация результатов упаковки
    visualizer = PlacedObjectsVisualizer(container)
    visualizer.visualize(placed_objects, title="Physics Packing Result")

    # Генерация инструкций для манипулятора (для случайных данных создаем фиктивные объекты детекции)
    # Для реальных данных используйте result.converted_objects
    fake_detected_objects = [
        type('RectObject', (), {
            'id': obj.id,
            'center_mm': (random.uniform(10, 50), random.uniform(10, 50)),
            'angle_deg': random.uniform(0, 360),
            'width': obj.width,
            'height': obj.height,
            'z': random.uniform(50, 100)
        })()
        for obj in random_objects
    ]

    # Координаты контейнера в реальном мире (мм)
    container_world_position = (100.0, 50.0)  # пример координат

    # Генерируем инструкции
    instruction_generator = ManipulatorInstructionGenerator(container_world_position)
    instructions, unpacked_ids = instruction_generator.generate_instructions(fake_detected_objects, placed_objects)

    # Сохраняем в JSON
    instruction_generator.save_to_json(instructions, unpacked_ids, output_dir + "manipulator_instructions.json")

    print(f"Generated {len(instructions)} manipulator instructions")
    if unpacked_ids:
        print(f"Unpacked objects (IDs): {unpacked_ids}")
    else:
        print("All objects were successfully packed!")

    # Визуализация исходного кадра с детекцией (для реальных данных)
    # visualizer = SceneProcessVisualizer()
    # visualized = visualizer.visualize(frame, result)
    # cv2.imshow("Scene", visualized)
    # cv2.waitKey(0)

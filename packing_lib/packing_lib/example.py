from typing import List
import random

import cv2
import numpy as np
from app.AppConfig import AppConfig
from packing_lib.packing_lib.SceneProcessor import SceneProcessor
from packing_lib.packing_lib.detectors.ArucoDetector import ArucoBoxDetector
from packing_lib.packing_lib.detectors.YoloBoxDetector import YoloBoxDetector
from packing_lib.packing_lib.manipulator.ManipulatorInstructionGenerator import ManipulatorInstructionGenerator
from packing_lib.packing_lib.packers.ExactORToolsPacker import ExactORToolsPacker
from packing_lib.packing_lib.packers.NFDHPacker import NFDHPacker
from packing_lib.packing_lib.packers.PhysPacker import PhysPacker
from packing_lib.packing_lib.types import SceneProcessResult, PackingInputTask, PackInputObject, PackingContainer
from packing_lib.packing_lib.visualization.PlacedObjectsVisualizer import PlacedObjectsVisualizer
from packing_lib.packing_lib.visualization.SceneProcessVisualizer import SceneProcessVisualizer


def generate_random_objects(count: int, min_size: float = 1.0, max_size: float = 4.0) -> List[PackInputObject]:
    """Генерирует случайный набор объектов для упаковки"""
    objects = []
    for i in range(count):
        width = random.uniform(min_size, max_size)
        height = random.uniform(min_size, max_size)
        objects.append(PackInputObject(id=i, width=width, height=height))
    return objects


def generate_fake_detected_objects(count: int, container: PackingContainer, min_size: float = 10.0, max_size: float = 80.0):
    """Генерирует фейковые объекты детекции для имитации реального сценария"""
    # Создаем фейковые RectObject (имитируем детекцию)
    fake_detected_objects = []
    for i in range(count):
        width = random.uniform(min_size, max_size)
        height = random.uniform(min_size, max_size)

        # Случайные координаты в области вне контейнера (имитируем стол с объектами)
        center_x = random.uniform(-50, container.width + 50)
        center_y = random.uniform(-50, container.height + 50)
        angle = random.uniform(0, 360)
        z = random.uniform(50, 100)

        # Создаем фейковый RectObject
        fake_object = type('RectObject', (), {
            'id': i,
            'center_mm': (center_x, center_y),
            'angle_deg': angle,
            'width': width,
            'height': height,
            'z': z
        })()
        fake_detected_objects.append(fake_object)
    return fake_detected_objects


if __name__ == "__main__":
    scale = 2
    container = PackingContainer(190 * scale, 110 * scale)
    input_dir = "../../in/"
    output_dir = "../../out/"

    frame = cv2.imread(input_dir + "det2.jpg")
    aruco = ArucoBoxDetector(23, AppConfig.camera_matrix, AppConfig.dist_coeffs)
    yolo = YoloBoxDetector()
    processor = SceneProcessor(aruco, yolo)
    result = processor.process(frame)
    detected_objects = result.converted_objects

    # Визуализация исходного кадра с детекцией (для реальных данных)
    visualizer = SceneProcessVisualizer()
    visualized = visualizer.visualize(frame, result)
    scale = 0.8
    resized = cv2.resize(visualized, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    cv2.imshow("Scene", resized)
    cv2.waitKey(0)

    # Генерируем фейковые объекты детекции (имитируем реальный сценарий)
    # detected_objects = generate_fake_detected_objects(
    #     count=40, container=container, min_size=10, max_size=80
    # )


    task = PackingInputTask(container, PackingInputTask.from_rect_objects(detected_objects))

    # Используем масштабирование для лучшей визуализации
    # Можно попробовать разные режимы:
    # packer = PhysPacker(headless=True)  # максимальная скорость
    # packer = PhysPacker(headless=False, simulation_speed=0.3)  # ускоренная визуализация
    # packer = PhysPacker(headless=False, simulation_speed=1.0)
    # packer = ExactORToolsPacker()
    packer = NFDHPacker()
    print("started")
    placed_objects = packer.pack(task)
    print("packed")

    # Визуализация результатов упаковки
    visualizer = PlacedObjectsVisualizer(container)
    visualizer.visualize(placed_objects, title="Physics Packing Result")

    # Генерация инструкций для манипулятора
    # Используем detected_objects (фейковые или реальные, в зависимости от режима)

    # Координаты контейнера в реальном мире (мм)
    container_world_position = (100.0, 50.0)  # пример координат

    # Генерируем инструкции
    instruction_generator = ManipulatorInstructionGenerator(container_world_position)
    instructions, unpacked_ids = instruction_generator.generate_instructions(detected_objects, placed_objects)

    # Сохраняем в JSON
    instruction_generator.save_to_json(instructions, unpacked_ids, output_dir + "manipulator_instructions.json")

    print(f"Generated {len(instructions)} manipulator instructions")
    if unpacked_ids:
        print(f"Unpacked objects (IDs): {unpacked_ids}")
    else:
        print("All objects were successfully packed!")


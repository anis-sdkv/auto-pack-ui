# from app.App import app_instance
#
# app_instance.run()
#
import cv2
from matplotlib import pyplot as plt

from app.AppConfig import AppConfig
from packing_lib.packing_lib.SceneProcessor import SceneProcessor
from packing_lib.packing_lib.detectors.ArucoDetector import ArucoBoxDetector
from packing_lib.packing_lib.detectors.YoloBoxDetector import YoloBoxDetector

import cv2
import numpy as np

from packing_lib.packing_lib.packers.NFDHPacker import NFDHPacker
from packing_lib.packing_lib.packers.PhysPacker import PhysPacker
from packing_lib.packing_lib.types import SceneProcessResult, PackingTask, Container

import cv2
import numpy as np
from packing_lib.packing_lib.types import SceneProcessResult


def visualize_scene_process_result(frame: np.ndarray, result: SceneProcessResult) -> np.ndarray:
    """
    Визуализирует результат SceneProcessResult:
    - рисует raw_objects в пикселях
    - подписывает реальные координаты и размеры из converted_objects
    - рисует ArUco-маркеры
    - помечает центр объекта кружком
    """
    annotated = frame.copy()

    # Настройки визуализации
    marker_color = (255, 0, 0)  # Синий
    object_color = (0, 255, 0)  # Зелёный
    text_color = (0, 0, 0)  # Чёрный
    center_color = (0, 0, 255)  # Красный кружок
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    thickness = 1
    circle_radius = 4

    # Индексируем converted_objects по id
    converted_map = {obj.id: obj for obj in result.converted_objects}

    # --- 1. Рисуем маркеры ---
    for marker in result.markers:
        pts = marker.bounding_box.astype(int)
        cv2.polylines(annotated, [pts], isClosed=True, color=marker_color, thickness=2)
        center = np.mean(pts, axis=0).astype(int)
        cv2.putText(annotated, f"ID:{marker.id}", tuple(center), font, font_scale, marker_color, thickness)

    # --- 2. Рисуем объекты ---
    for raw in result.raw_objects:
        obj_id = raw.id
        rect = raw.bounding_box  # ((cx, cy), (w, h), angle)

        box = cv2.boxPoints(rect)
        box = np.int32(box)
        cv2.polylines(annotated, [box], isClosed=True, color=object_color, thickness=2)

        if obj_id in converted_map:
            converted = converted_map[obj_id]
            cx, cy = converted.center_mm
            w, h = converted.width, converted.height
            angle = converted.angle_deg

            label = (
                f"id:{obj_id} "
                f"C=({cx:.1f},{cy:.1f}) "
                f"S={w:.2f}x{h:.2f} mm "
                f"A={int(angle)}°"
            )

            # Центр по среднему bbox
            center_px = tuple(np.mean(box, axis=0).astype(int))
            cv2.circle(annotated, center_px, circle_radius, center_color, -1)

            # Текст рядом с центром
            text_pos = (center_px[0] + 5, center_px[1] - 5)
            cv2.putText(annotated, label, text_pos, font, font_scale, text_color, thickness, cv2.LINE_AA)

    return annotated


import cv2
import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class PlacedObject:
    id: int
    x: float
    y: float
    width: float
    height: float

def visualize_objects(objects: List[PlacedObject], title: str = "Placed Objects"):
    fig, ax = plt.subplots()

    for obj in objects:
        rect = plt.Rectangle((obj.x, obj.y), obj.width, obj.height,
                             fill=False, edgecolor='blue', linewidth=2)
        ax.add_patch(rect)
        ax.text(obj.x + obj.width / 2, obj.y + obj.height / 2, str(obj.id),
                ha='center', va='center', fontsize=10, color='red')

    ax.set_aspect('equal')
    ax.set_xlim(min(o.x for o in objects) - 10, max(o.x + o.width for o in objects) + 10)
    ax.set_ylim(min(o.y for o in objects) - 10, max(o.y + o.height for o in objects) + 10)
    plt.gca().invert_yaxis()
    ax.set_title(title)
    plt.grid(True)
    plt.show()


frame = cv2.imread("in/det7.jpg")
aruco = ArucoBoxDetector(2.3, AppConfig.camera_matrix, AppConfig.dist_coeffs)
yolo = YoloBoxDetector()
processor = SceneProcessor(aruco, yolo)
result = processor.process(frame)

task = PackingTask(
    Container((0, 50), 19, 11),
    result.converted_objects
)

packer = NFDHPacker()
placed_objects = packer.pack(task)


visualize_objects(placed_objects)
visualized = visualize_scene_process_result(frame, result)
cv2.imshow("Scene", visualized)
cv2.waitKey(0)

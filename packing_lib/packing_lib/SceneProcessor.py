from typing import List, Tuple, Optional

import cv2
import numpy as np

from packing_lib.packing_lib.types import SceneProcessResult, RectObject, ArucoResult


class SceneProcessor:
    def __init__(self, aruco_detector, yolo_detector):
        self.aruco_detector = aruco_detector
        self.yolo_detector = yolo_detector
        self.angle_tolerance = 15.0

    def process(self, image) -> SceneProcessResult:
        arucos = self.aruco_detector.detect(image)
        detected = self.yolo_detector.detect(image)
        filtered_objects = SceneProcessor.filter_by_overlap(detected, [m.bounding_box for m in arucos])
        converted_objects: List[RectObject] = []
        reference_marker = self._validate_and_get_reference_marker(arucos)
        scale = None

        if reference_marker is not None:
            aruco_center_px = self._get_aruco_center(reference_marker)
            scale = self._estimate_scale(reference_marker)
            scene_x_axis_angle = self._calculate_scene_x_axis_angle(arucos)

            for raw_obj in filtered_objects:
                (cx, cy), (w, h), angle = raw_obj.bounding_box
                object_center_px = np.array([cx, cy])

                object_pos_mm = self._pixel_to_mm_coordinates(
                    aruco_center_px, object_center_px, scale
                )

                w_mm, h_mm = w * scale, h * scale
                
                # Корректируем угол относительно оси X сцены
                corrected_angle = self._correct_angle_relative_to_scene(angle, scene_x_axis_angle)

                converted_objects.append(
                    RectObject(
                        id=raw_obj.id,
                        center_mm=tuple(object_pos_mm),
                        angle_deg=corrected_angle,
                        width=w_mm,
                        height=h_mm,
                        z=0
                    )
                )

        return SceneProcessResult(
            markers=arucos,
            raw_objects=filtered_objects,
            converted_objects=converted_objects,
            reference_marker=reference_marker,
            scale=scale if reference_marker else None
        )

    def _validate_and_get_reference_marker(self, arucos: List[ArucoResult]) -> Optional[ArucoResult]:
        """
        Проверяет, что маркеры расположены в правильной конфигурации:
        - Ровно 3 маркера
        - Слева сверху, справа сверху, слева снизу
        - Углы между линиями близки к 90°

        Возвращает референсный маркер (левый верхний) или None, если конфигурация неверная
        """
        if len(arucos) != 3:
            return None

        # Получаем центры маркеров
        centers = [self._get_aruco_center(aruco) for aruco in arucos]

        # Сортируем маркеры по позиции для определения их расположения
        markers_with_centers = list(zip(arucos, centers))

        # Находим кандидатов на каждую позицию
        top_left, top_right, bottom_left = self._identify_marker_positions(markers_with_centers)

        if top_left is None or top_right is None or bottom_left is None:
            return None

        if self._validate_rectangle_angles(top_left[1], top_right[1], bottom_left[1]):
            return top_left[0]

        return None

    def _identify_marker_positions(self, markers_with_centers: List[Tuple[ArucoResult, np.ndarray]]) -> Tuple[
        Optional[Tuple[ArucoResult, np.ndarray]], Optional[Tuple[ArucoResult, np.ndarray]], Optional[
            Tuple[ArucoResult, np.ndarray]]]:
        """
        Определяет позиции маркеров: левый верхний, правый верхний, левый нижний
        """
        if len(markers_with_centers) != 3:
            return None, None, None

        sorted_by_y = sorted(markers_with_centers, key=lambda x: x[1][1])

        top_markers = sorted_by_y[:2]
        top_markers_sorted = sorted(top_markers, key=lambda x: x[1][0])

        bottom_marker = sorted_by_y[2]

        top_left_candidate = top_markers_sorted[0]
        top_right_candidate = top_markers_sorted[1]
        bottom_candidate = bottom_marker

        if abs(bottom_candidate[1][0] - top_left_candidate[1][0]) > abs(
                bottom_candidate[1][0] - top_right_candidate[1][0]):
            return None, None, None

        return top_left_candidate, top_right_candidate, bottom_candidate

    def _validate_rectangle_angles(self, top_left: np.ndarray, top_right: np.ndarray, bottom_left: np.ndarray) -> bool:
        """
        Проверяет, что углы между линиями близки к 90°
        """
        vec_to_right = top_right - top_left
        vec_to_bottom = bottom_left - top_left

        dot_product = np.dot(vec_to_right, vec_to_bottom)
        norm_right = np.linalg.norm(vec_to_right)
        norm_bottom = np.linalg.norm(vec_to_bottom)

        if norm_right == 0 or norm_bottom == 0:
            return False

        cos_angle = dot_product / (norm_right * norm_bottom)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle_deg = np.degrees(np.arccos(abs(cos_angle)))

        return abs(angle_deg - 90.0) <= self.angle_tolerance

    def _get_aruco_center(self, aruco: ArucoResult) -> np.ndarray:
        """Получает координаты центра ArUco маркера в пикселях"""
        corners = aruco.bounding_box
        center = np.mean(corners, axis=0)
        return center

    def _estimate_scale(self, aruco: ArucoResult) -> float:
        """Оценивает масштаб мм/пиксель на основе размера ArUco маркера"""
        corners = aruco.bounding_box

        edge1_px = np.linalg.norm(corners[1] - corners[0])
        edge2_px = np.linalg.norm(corners[2] - corners[1])
        pixel_size_marker = (edge1_px + edge2_px) / 2

        return self.aruco_detector.aruco_size_mm / pixel_size_marker

    def _pixel_to_mm_coordinates(self, aruco_center_px: np.ndarray,
                                 object_center_px: np.ndarray, scale: float) -> np.ndarray:
        """
        Преобразует координаты объекта из пикселей в миллиметры
        относительно центра ArUco маркера

        Args:
            aruco_center_px: координаты центра маркера в пикселях [x0, y0]
            object_center_px: координаты центра объекта в пикселях [xi, yi]
            scale: масштаб мм/пиксель

        Returns:
            координаты объекта в мм относительно центра маркера
        """
        # 1. Разница координат (в пикселях)
        delta = object_center_px - aruco_center_px

        # 2. Перевод в мм
        object_pos_mm = delta * scale

        return object_pos_mm

    def _calculate_scene_x_axis_angle(self, arucos: List[ArucoResult]) -> float:
        """
        Вычисляет угол оси X сцены относительно горизонтальной оси изображения
        Ось X определяется как линия между центрами левого верхнего и правого верхнего ArUco маркеров
        
        Returns:
            Угол в градусах (0-360)
        """
        if len(arucos) < 3:
            return 0.0
            
        # Получаем центры маркеров
        centers = [self._get_aruco_center(aruco) for aruco in arucos]
        markers_with_centers = list(zip(arucos, centers))
        
        # Находим позиции маркеров
        top_left, top_right, bottom_left = self._identify_marker_positions(markers_with_centers)
        
        if top_left is None or top_right is None:
            return 0.0
            
        # Вектор оси X сцены (от левого верхнего к правому верхнему маркеру)
        scene_x_vector = top_right[1] - top_left[1]
        
        # Вычисляем угол относительно горизонтальной оси изображения
        angle_rad = np.arctan2(scene_x_vector[1], scene_x_vector[0])
        angle_deg = np.degrees(angle_rad)
        
        # Нормализуем к диапазону [0, 360)
        if angle_deg < 0:
            angle_deg += 360
            
        return angle_deg

    def _correct_angle_relative_to_scene(self, object_angle: float, scene_x_axis_angle: float) -> float:
        """
        Корректирует угол объекта относительно оси X сцены
        
        Args:
            object_angle: угол объекта в системе координат изображения (градусы)
            scene_x_axis_angle: угол оси X сцены относительно горизонтали изображения (градусы)
            
        Returns:
            Скорректированный угол в системе координат сцены (градусы, 0-180)
        """
        # Корректируем угол объекта относительно оси X сцены
        corrected_angle = object_angle - scene_x_axis_angle
        
        # Нормализуем к диапазону [0, 180)
        corrected_angle = corrected_angle % 180
        
        return corrected_angle

    @staticmethod
    def box_inside_area_ratio(inner_box: np.ndarray, outer_box: np.ndarray) -> float:
        """Вычисляет долю площади inner_box, которая находится внутри outer_box"""
        inner_box = np.array(inner_box, dtype=np.float32)
        outer_box = np.array(outer_box, dtype=np.float32)

        inter_area, _ = cv2.intersectConvexConvex(inner_box, outer_box)
        inner_area = cv2.contourArea(inner_box)

        if inner_area == 0:
            return 0.0

        return inter_area / inner_area

    @staticmethod
    def filter_by_overlap(source_list, remove_list, threshold=0.8):
        """Фильтрует объекты, которые сильно перекрываются с маркерами"""
        filtered = []
        for src in source_list:
            if not any(SceneProcessor.box_inside_area_ratio(rem, cv2.boxPoints(src.bounding_box)) > threshold
                       for rem in remove_list):
                filtered.append(src)
        return filtered
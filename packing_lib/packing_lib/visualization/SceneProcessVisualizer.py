import cv2
import numpy as np
import math
from typing import List, Tuple

from packing_lib.packing_lib.types import SceneProcessResult, RectObject, ArucoResult


class SceneProcessVisualizer:
    """Визуализатор результатов обработки сцены с детекцией объектов и ArUco маркеров"""
    
    def __init__(self, font_scale: float = 0.5, thickness: int = 2):
        self.font_scale = font_scale
        self.thickness = thickness
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Цвета
        self.marker_color = (255, 0, 0)      # Синий для маркеров
        self.object_color = (0, 255, 0)      # Зеленый для объектов
        self.center_color = (0, 0, 255)      # Красный для центров
        self.x_axis_color = (255, 255, 0)    # Голубой для оси X
        self.origin_color = (255, 0, 255)    # Магента для начала координат
        self.text_color = (255, 255, 255)    # Белый для текста
        
    def visualize(self, image: np.ndarray, result: SceneProcessResult) -> np.ndarray:
        """
        Визуализирует результат обработки сцены
        
        Args:
            image: Исходное изображение
            result: Результат обработки сцены
            
        Returns:
            Изображение с визуализацией
        """
        vis_img = image.copy()
        
        # Получаем параметры масштабирования для обратного преобразования координат
        reference_marker = result.reference_marker
        scale = result.scale
        aruco_center_px = None
        
        if len(result.markers) >= 3:
            # Находим позиции маркеров для определения системы координат
            marker_positions = self._identify_marker_positions(result.markers)
            
            # Отрисовываем маркеры
            self._draw_markers(vis_img, result.markers, marker_positions)
            
            # Отрисовываем ось X и начало координат
            if marker_positions['top_left'] and marker_positions['top_right']:
                self._draw_coordinate_system(vis_img, marker_positions)
                
                # Получаем центр референсного маркера
                if reference_marker:
                    aruco_center_px = self._get_aruco_center(reference_marker)
        
        # Отрисовываем объекты с правильным преобразованием координат
        self._draw_objects(vis_img, result.converted_objects, aruco_center_px, scale)
        
        return vis_img
    
    def _identify_marker_positions(self, markers: List[ArucoResult]) -> dict:
        """Определяет позиции маркеров в сцене"""
        if len(markers) != 3:
            return {'top_left': None, 'top_right': None, 'bottom_left': None}
        
        # Получаем центры маркеров
        centers = [self._get_aruco_center(marker) for marker in markers]
        markers_with_centers = list(zip(markers, centers))
        
        # Сортируем по Y (верхние и нижний)
        sorted_by_y = sorted(markers_with_centers, key=lambda x: x[1][1])
        
        # Верхние два маркера
        top_markers = sorted_by_y[:2]
        top_markers_sorted = sorted(top_markers, key=lambda x: x[1][0])  # по X
        
        bottom_marker = sorted_by_y[2]
        
        # Проверяем правильность конфигурации
        top_left_candidate = top_markers_sorted[0]
        top_right_candidate = top_markers_sorted[1]
        bottom_candidate = bottom_marker
        
        # Нижний маркер должен быть ближе к левому верхнему
        if abs(bottom_candidate[1][0] - top_left_candidate[1][0]) <= abs(
                bottom_candidate[1][0] - top_right_candidate[1][0]):
            return {
                'top_left': top_left_candidate,
                'top_right': top_right_candidate,
                'bottom_left': bottom_candidate
            }
        
        return {'top_left': None, 'top_right': None, 'bottom_left': None}
    
    def _get_aruco_center(self, marker: ArucoResult) -> np.ndarray:
        """Получает центр ArUco маркера"""
        corners = marker.bounding_box
        center = np.mean(corners, axis=0)
        return center.astype(int)
    
    
    def _draw_markers(self, img: np.ndarray, markers: List[ArucoResult], positions: dict):
        """Отрисовывает ArUco маркеры"""
        for marker in markers:
            # Рисуем контур маркера
            corners = marker.bounding_box.astype(int)
            cv2.polylines(img, [corners], True, self.marker_color, self.thickness)
            
            # Отмечаем центр маркера
            center = self._get_aruco_center(marker)
            cv2.circle(img, tuple(center), 5, self.center_color, -1)
            
            # Подписываем ID маркера
            self._draw_text_with_outline(img, f"M{marker.id}", 
                                       (center[0] + 10, center[1] - 10),
                                       self.font, self.font_scale, self.text_color, (0, 0, 0), 1)
        
        # Подписываем позиции маркеров
        if positions['top_left']:
            center = self._get_aruco_center(positions['top_left'][0])
            self._draw_text_with_outline(img, "TL", (center[0] - 30, center[1]), 
                                       self.font, self.font_scale, self.text_color, (0, 0, 0), 1)
        
        if positions['top_right']:
            center = self._get_aruco_center(positions['top_right'][0])
            self._draw_text_with_outline(img, "TR", (center[0] + 15, center[1]), 
                                       self.font, self.font_scale, self.text_color, (0, 0, 0), 1)
        
        if positions['bottom_left']:
            center = self._get_aruco_center(positions['bottom_left'][0])
            self._draw_text_with_outline(img, "BL", (center[0] - 30, center[1] + 20), 
                                       self.font, self.font_scale, self.text_color, (0, 0, 0), 1)
    
    def _draw_coordinate_system(self, img: np.ndarray, positions: dict):
        """Отрисовывает систему координат и ось X"""
        if not positions['top_left'] or not positions['top_right']:
            return
        
        tl_center = self._get_aruco_center(positions['top_left'][0])
        tr_center = self._get_aruco_center(positions['top_right'][0])
        
        # Рисуем ось X (линия между верхними маркерами)
        cv2.line(img, tuple(tl_center), tuple(tr_center), self.x_axis_color, self.thickness)
        
        # Стрелка на конце оси X
        self._draw_arrow(img, tl_center, tr_center, self.x_axis_color)
        
        # Подписываем ось X
        mid_point = ((tl_center[0] + tr_center[0]) // 2, (tl_center[1] + tr_center[1]) // 2)
        self._draw_text_with_outline(img, "X axis", (mid_point[0], mid_point[1] - 15), 
                                   self.font, self.font_scale, self.x_axis_color, (0, 0, 0), 1)
        
        # Отмечаем начало координат (центр левого верхнего маркера)
        cv2.circle(img, tuple(tl_center), 8, self.origin_color, 2)
        self._draw_text_with_outline(img, "Origin (0,0)", (tl_center[0] + 15, tl_center[1] + 15), 
                                   self.font, self.font_scale, self.origin_color, (0, 0, 0), 1)
    
    def _draw_arrow(self, img: np.ndarray, start: np.ndarray, end: np.ndarray, color: tuple):
        """Рисует стрелку на конце линии"""
        # Вычисляем направление
        direction = end - start
        length = np.linalg.norm(direction)
        if length == 0:
            return
        
        unit_dir = direction / length
        
        # Стрелка длиной 15 пикселей
        arrow_length = 15
        arrow_angle = np.pi / 6  # 30 градусов
        
        # Концы стрелки
        arrow_p1 = end - arrow_length * (unit_dir * np.cos(arrow_angle) + 
                                        np.array([-unit_dir[1], unit_dir[0]]) * np.sin(arrow_angle))
        arrow_p2 = end - arrow_length * (unit_dir * np.cos(arrow_angle) - 
                                        np.array([-unit_dir[1], unit_dir[0]]) * np.sin(arrow_angle))
        
        cv2.line(img, tuple(end.astype(int)), tuple(arrow_p1.astype(int)), color, 1)
        cv2.line(img, tuple(end.astype(int)), tuple(arrow_p2.astype(int)), color, 1)
    
    def _draw_objects(self, img: np.ndarray, objects: List[RectObject], 
                     aruco_center_px: np.ndarray = None, scale: float = None):
        """Отрисовывает детектированные объекты"""
        for obj in objects:
            self._draw_single_object(img, obj, aruco_center_px, scale)
    
    def _draw_single_object(self, img: np.ndarray, obj: RectObject, 
                           aruco_center_px: np.ndarray = None, scale: float = None):
        """Отрисовывает один объект с подробной информацией"""
        
        # Преобразуем координаты из мм обратно в пиксели
        if aruco_center_px is not None and scale is not None:
            # Обратное преобразование: мм → пиксели
            object_pos_mm = np.array([obj.center_mm[0], obj.center_mm[1]])
            object_pos_px = object_pos_mm / scale + aruco_center_px
            center_px = object_pos_px.astype(int)
            
            # Размеры в пикселях
            width_px = obj.width / scale
            height_px = obj.height / scale
        else:
            # Fallback: используем мм как пиксели (для отладки)
            center_px = np.array([obj.center_mm[0], obj.center_mm[1]], dtype=int)
            width_px = obj.width
            height_px = obj.height
        
        # Вычисляем угол в радианах
        angle_rad = np.radians(obj.angle_deg)
        
        # Половинные размеры в пикселях
        half_w = width_px / 2
        half_h = height_px / 2
        
        # Углы прямоугольника в локальной системе координат
        corners_local = np.array([
            [-half_w, -half_h],  # левый верхний
            [half_w, -half_h],   # правый верхний
            [half_w, half_h],    # правый нижний
            [-half_w, half_h]    # левый нижний
        ])
        
        # Поворачиваем углы
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        corners_rotated = corners_local @ rotation_matrix.T
        
        # Переносим в глобальные координаты
        corners_global = corners_rotated + center_px
        corners_int = corners_global.astype(int)
        
        # Рисуем контур объекта
        cv2.polylines(img, [corners_int], True, self.object_color, self.thickness)
        
        # Отмечаем центр объекта
        cv2.circle(img, tuple(center_px), 3, self.center_color, -1)
        
        # Рисуем линию вдоль всей высоты (параллельно короткой стороне)
        # Высота = короткая сторона, поэтому линия между центрами верхней и нижней сторон
        top_center = (corners_int[0] + corners_int[1]) // 2
        bottom_center = (corners_int[2] + corners_int[3]) // 2
        cv2.line(img, tuple(top_center), tuple(bottom_center), self.center_color, 1)
        
        # Подписываем размеры (показываем реальные размеры в мм)
        self._draw_dimension_labels(img, corners_int, obj.width, obj.height, angle_rad)
        
        # Подписываем информацию об объекте
        info_text = f"ID:{obj.id} ({obj.center_mm[0]:.1f},{obj.center_mm[1]:.1f}) {obj.angle_deg:.1f}°"
        text_pos = (center_px[0] + 5, center_px[1] - 5)
        
        # Текст с черной обводкой
        self._draw_text_with_outline(img, info_text, text_pos, self.font, 
                                   self.font_scale * 0.7, self.text_color, (0, 0, 0), 1)
    
    def _draw_dimension_labels(self, img: np.ndarray, corners: np.ndarray, 
                              width: float, height: float, angle_rad: float):
        """Подписывает размеры объекта вдоль сторон"""
        # Центры сторон
        top_center = (corners[0] + corners[1]) // 2
        right_center = (corners[1] + corners[2]) // 2
        bottom_center = (corners[2] + corners[3]) // 2
        left_center = (corners[3] + corners[0]) // 2
        
        # Подписываем ширину (вдоль верхней стороны)
        width_text = f"w={width:.1f}"
        self._draw_text_with_outline(img, width_text, tuple(top_center), self.font, 
                                   self.font_scale * 0.6, self.text_color, (0, 0, 0), 1)
        
        # Подписываем высоту (вдоль правой стороны)
        height_text = f"h={height:.1f}"
        self._draw_text_with_outline(img, height_text, tuple(right_center), self.font, 
                                   self.font_scale * 0.6, self.text_color, (0, 0, 0), 1)
    
    def _draw_text_with_outline(self, img: np.ndarray, text: str, position: tuple, 
                               font, font_scale: float, text_color: tuple, outline_color: tuple, thickness: int):
        """Рисует текст с черной обводкой"""
        x, y = position
        
        # Рисуем обводку (черный текст толщиной thickness + 2)
        cv2.putText(img, text, (x, y), font, font_scale, outline_color, thickness + 2)
        
        # Рисуем основной текст поверх обводки
        cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)

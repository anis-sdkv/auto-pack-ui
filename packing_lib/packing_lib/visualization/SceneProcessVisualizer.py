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
        self.marker_color = (255, 0, 0)
        self.object_color = (0, 255, 0)
        self.center_color = (0, 0, 255)
        self.x_axis_color = (255, 255, 0)
        self.origin_color = (255, 0, 255)
        self.text_color = (255, 255, 255)

    def visualize(self, image: np.ndarray, result: SceneProcessResult) -> np.ndarray:

        vis_img = image.copy()

        reference_marker = result.reference_marker
        scale = result.scale
        aruco_center_px = None

        if len(result.markers) >= 3:
            marker_positions = self._identify_marker_positions(result.markers)

            self._draw_markers(vis_img, result.markers, marker_positions)

            if marker_positions['top_left'] and marker_positions['top_right']:
                self._draw_coordinate_system(vis_img, marker_positions)

                if reference_marker:
                    aruco_center_px = self._get_aruco_center(reference_marker)

        self._draw_objects(vis_img, result.converted_objects, aruco_center_px, scale)

        return vis_img

    def _identify_marker_positions(self, markers: List[ArucoResult]) -> dict:
        if len(markers) != 3:
            return {'top_left': None, 'top_right': None, 'bottom_left': None}

        centers = [self._get_aruco_center(marker) for marker in markers]
        markers_with_centers = list(zip(markers, centers))

        sorted_by_y = sorted(markers_with_centers, key=lambda x: x[1][1])

        top_markers = sorted_by_y[:2]
        top_markers_sorted = sorted(top_markers, key=lambda x: x[1][0])  # по X

        bottom_marker = sorted_by_y[2]

        top_left_candidate = top_markers_sorted[0]
        top_right_candidate = top_markers_sorted[1]
        bottom_candidate = bottom_marker

        if abs(bottom_candidate[1][0] - top_left_candidate[1][0]) <= abs(
                bottom_candidate[1][0] - top_right_candidate[1][0]):
            return {
                'top_left': top_left_candidate,
                'top_right': top_right_candidate,
                'bottom_left': bottom_candidate
            }

        return {'top_left': None, 'top_right': None, 'bottom_left': None}

    def _get_aruco_center(self, marker: ArucoResult) -> np.ndarray:
        corners = marker.bounding_box
        center = np.mean(corners, axis=0)
        return center.astype(int)


    def _draw_markers(self, img: np.ndarray, markers: List[ArucoResult], positions: dict):
        for marker in markers:
            corners = marker.bounding_box.astype(int)
            cv2.polylines(img, [corners], True, self.marker_color, self.thickness)

            center = self._get_aruco_center(marker)
            cv2.circle(img, tuple(center), 5, self.center_color, -1)

            self._draw_text_with_outline(img, f"M{marker.id}",
                                       (center[0] + 10, center[1] - 10),
                                       self.font, self.font_scale, self.text_color, (0, 0, 0), 1)

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
        if not positions['top_left'] or not positions['top_right']:
            return

        tl_center = self._get_aruco_center(positions['top_left'][0])
        tr_center = self._get_aruco_center(positions['top_right'][0])

        cv2.line(img, tuple(tl_center), tuple(tr_center), self.x_axis_color, self.thickness)

        self._draw_arrow(img, tl_center, tr_center, self.x_axis_color)

        mid_point = ((tl_center[0] + tr_center[0]) // 2, (tl_center[1] + tr_center[1]) // 2)
        self._draw_text_with_outline(img, "X axis", (mid_point[0], mid_point[1] - 15),
                                   self.font, self.font_scale, self.x_axis_color, (0, 0, 0), 1)

        cv2.circle(img, tuple(tl_center), 8, self.origin_color, 2)
        self._draw_text_with_outline(img, "Origin (0,0)", (tl_center[0] + 15, tl_center[1] + 15),
                                   self.font, self.font_scale, self.origin_color, (0, 0, 0), 1)

    def _draw_arrow(self, img: np.ndarray, start: np.ndarray, end: np.ndarray, color: tuple):
        direction = end - start
        length = np.linalg.norm(direction)
        if length == 0:
            return

        unit_dir = direction / length

        arrow_length = 15
        arrow_angle = np.pi / 6

        arrow_p1 = end - arrow_length * (unit_dir * np.cos(arrow_angle) +
                                        np.array([-unit_dir[1], unit_dir[0]]) * np.sin(arrow_angle))
        arrow_p2 = end - arrow_length * (unit_dir * np.cos(arrow_angle) -
                                        np.array([-unit_dir[1], unit_dir[0]]) * np.sin(arrow_angle))

        cv2.line(img, tuple(end.astype(int)), tuple(arrow_p1.astype(int)), color, 1)
        cv2.line(img, tuple(end.astype(int)), tuple(arrow_p2.astype(int)), color, 1)

    def _draw_objects(self, img: np.ndarray, objects: List[RectObject],
                     aruco_center_px: np.ndarray = None, scale: float = None):
        for obj in objects:
            self._draw_single_object(img, obj, aruco_center_px, scale)

    def _draw_single_object(self, img: np.ndarray, obj: RectObject,
                           aruco_center_px: np.ndarray = None, scale: float = None):

        if aruco_center_px is not None and scale is not None:
            object_pos_mm = np.array([obj.center_mm[0], obj.center_mm[1]])
            object_pos_px = object_pos_mm / scale + aruco_center_px
            center_px = object_pos_px.astype(int)

            width_px = obj.width / scale
            height_px = obj.height / scale
        else:
            center_px = np.array([obj.center_mm[0], obj.center_mm[1]], dtype=int)
            width_px = obj.width
            height_px = obj.height

        angle_rad = np.radians(obj.angle_deg)

        half_w = width_px / 2
        half_h = height_px / 2

        corners_local = np.array([
            [-half_w, -half_h],
            [half_w, -half_h],
            [half_w, half_h],
            [-half_w, half_h]
        ])

        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        corners_rotated = corners_local @ rotation_matrix.T

        corners_global = corners_rotated + center_px
        corners_int = corners_global.astype(int)

        cv2.polylines(img, [corners_int], True, self.object_color, self.thickness)

        cv2.circle(img, tuple(center_px), 3, self.center_color, -1)

        top_center = (corners_int[0] + corners_int[1]) // 2
        bottom_center = (corners_int[2] + corners_int[3]) // 2
        cv2.line(img, tuple(top_center), tuple(bottom_center), self.center_color, 1)

        self._draw_dimension_labels(img, corners_int, obj.width, obj.height, angle_rad)

        info_text = f"ID:{obj.id} ({obj.center_mm[0]:.1f},{obj.center_mm[1]:.1f}) {obj.angle_deg:.1f}°"
        text_pos = (center_px[0] + 5, center_px[1] - 5)

        self._draw_text_with_outline(img, info_text, text_pos, self.font,
                                   self.font_scale * 0.7, self.text_color, (0, 0, 0), 1)

    def _draw_dimension_labels(self, img: np.ndarray, corners: np.ndarray,
                              width: float, height: float, angle_rad: float):
        top_center = (corners[0] + corners[1]) // 2
        right_center = (corners[1] + corners[2]) // 2
        bottom_center = (corners[2] + corners[3]) // 2
        left_center = (corners[3] + corners[0]) // 2

        width_text = f"w={width:.1f}"
        self._draw_text_with_outline(img, width_text, tuple(top_center), self.font,
                                   self.font_scale * 0.6, self.text_color, (0, 0, 0), 1)

        height_text = f"h={height:.1f}"
        self._draw_text_with_outline(img, height_text, tuple(right_center), self.font,
                                   self.font_scale * 0.6, self.text_color, (0, 0, 0), 1)

    def _draw_text_with_outline(self, img: np.ndarray, text: str, position: tuple,
                               font, font_scale: float, text_color: tuple, outline_color: tuple, thickness: int):
        x, y = position

        cv2.putText(img, text, (x, y), font, font_scale, outline_color, thickness + 2)

        cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)

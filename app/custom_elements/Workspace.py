import random
from typing import List, Tuple

import cv2
import numpy
import numpy as np
import pygame

from app.common import Colors
from packing_lib.packing_lib.types import ArucoResult, RawObject, RectObject, PackInputObject


class Workspace:
    def __init__(self, rect: pygame.Rect):

        self.fill_color = Colors.WHITE
        self.border_color = Colors.BLACK
        self.border_width = 2

        self.generated_boxes: List[Tuple[pygame.Rect, Tuple[int, int, int]]] = []  # (rect, color)
        self.detected_boxes: List[RectObject] = []

        self.boxes: List[RawObject] = []
        self.converted_boxes: List[PackInputObject] = []

        self.detected_markers: List[ArucoResult] = []
        self.is_calibrated = False

        self.camera_frame: numpy.ndarray | None = None
        self._camera_frame_scale_factor = 1
        self.camera_width = None
        self.camera_resolution_ratio = 1

        self.update_rect(rect)

    def update_rect(self, rect: pygame.Rect):
        self.rect = rect
        self.subsurface = pygame.Surface(rect.size)
        self._recalculate_scale_ratio()

    def set_camera_resolution(self, width, height):
        self.camera_resolution_ratio = height / width
        self.camera_width = width
        self._recalculate_scale_ratio()

    def create_random_items(self, count: int):
        for i in range(count):
            width, height = random.randint(30, 100), random.randint(30, 100)
            x_pos = random.randint(0, self.rect.width - width)
            y_pos = random.randint(0, self.rect.height - height)
            color = random.choice(Colors.RECTANGLE_COLORS)

            self.generated_boxes.append((pygame.Rect(x_pos, y_pos, width, height), color))

    def draw(self, surface: pygame.Surface):
        surface.blit(self._render(), self.rect.topleft)

    def _recalculate_scale_ratio(self):
        self._camera_frame_scale_factor = 1 if self.camera_width is None else self.rect.width / self.camera_width

    def _render(self):
        self.subsurface.fill(self.fill_color)
        if self.camera_frame is not None:
            self._draw_camera_frame()
        else:
            self._draw_generated_boxes()
        pygame.draw.rect(self.subsurface, self.border_color, (0, 0, self.rect.w, self.rect.h), self.border_width)
        return self.subsurface

    def _draw_camera_frame(self):
        if self.camera_frame is None:
            return

        frame_rgb = cv2.cvtColor(self.camera_frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.fliplr(frame_rgb)

        target_size = tuple(map(int, (np.array(frame_rgb.shape[1::-1]) * self._camera_frame_scale_factor)))
        frame_rgb_scaled = cv2.resize(frame_rgb, target_size, interpolation=cv2.INTER_AREA)

        image_surface = pygame.surfarray.make_surface(np.rot90(frame_rgb_scaled))
        self.subsurface.blit(image_surface, (0, 0))
        self._draw_boxes()
        self._draw_markers()
        self._draw_calibration_indicator()

    def _draw_markers(self):
        for marker in self.detected_markers:
            points = (marker.bounding_box * self._camera_frame_scale_factor).astype(int).tolist()
            pygame.draw.polygon(self.subsurface, Colors.BLUE, points, 2)

    def _draw_boxes(self):
        for rect in self.boxes:
            box_points = cv2.boxPoints(rect.bounding_box)
            points = (box_points * self._camera_frame_scale_factor).astype(int).tolist()
            pygame.draw.polygon(self.subsurface, Colors.GREEN, points, 2)

    def _draw_generated_boxes(self):
        for rect, color in self.generated_boxes:
            pygame.draw.rect(self.subsurface, color, rect)
            pygame.draw.rect(self.subsurface, Colors.BLACK, rect, 1)
    
    def _draw_calibration_indicator(self):
        """Отрисовывает индикатор статуса калибровки поверх изображения"""
        # Позиция индикатора в правом верхнем углу
        indicator_size = 15
        margin = 10
        x = self.rect.width - indicator_size - margin
        y = margin
        
        # Цвет зависит от статуса калибровки
        color = Colors.GREEN if self.is_calibrated else Colors.RED
        
        # Рисуем круглый индикатор поверх изображения
        center = (x + indicator_size // 2, y + indicator_size // 2)
        pygame.draw.circle(self.subsurface, color, center, indicator_size // 2)
        pygame.draw.circle(self.subsurface, Colors.BLACK, center, indicator_size // 2, 2)

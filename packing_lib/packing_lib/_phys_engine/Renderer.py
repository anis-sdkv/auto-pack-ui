from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
import numpy as np
import random

import pygame
import pymunk
import math

from app.common import Colors
from packing_lib.packing_lib.types import PackingContainer


class Renderer(ABC):
    @abstractmethod
    def initialize(self, container: PackingContainer) -> Optional[pygame.Surface]:
        pass
    
    @abstractmethod
    def render(self, rectangles: List, segments: List) -> Optional[pygame.Surface]:
        pass
    
    @abstractmethod
    def cleanup(self):
        pass


class PygameRenderer(Renderer):
    def __init__(self, pixels_per_mm: float = 10.0):
        self._subsurface = None
        self._container = None
        self.pixels_per_mm = pixels_per_mm
    
    @staticmethod
    def _get_color_for_id(obj_id: int) -> Tuple[int, int, int]:
        """Генерирует стабильный цвет для объекта по его ID"""
        rng = random.Random(obj_id)
        return (rng.randint(50, 255), rng.randint(50, 255), rng.randint(50, 255))
        
    def initialize(self, container: PackingContainer) -> Optional[pygame.Surface]:
        self._container = container
        # Масштабируем размер поверхности для отрисовки
        width = int(container.width * self.pixels_per_mm)
        height = int(container.height * self.pixels_per_mm)
        self._subsurface = pygame.Surface((width, height))
        return self._subsurface
    
    def render(self, rectangles: List, segments: List) -> Optional[pygame.Surface]:
        if not self._subsurface:
            return None
            
        self._subsurface.fill(Colors.WHITE)

        # Масштабируем координаты сегментов
        for seg in segments:
            start = int(seg.a.x * self.pixels_per_mm), int(seg.a.y * self.pixels_per_mm)
            end = int(seg.b.x * self.pixels_per_mm), int(seg.b.y * self.pixels_per_mm)
            pygame.draw.line(self._subsurface, (23, 22, 110), start, end, max(1, int(3 * self.pixels_per_mm / 10)))

        # Масштабируем объекты
        for rect, body, shape in rectangles:
            width = max(1, int(rect.width * self.pixels_per_mm))
            height = max(1, int(rect.height * self.pixels_per_mm))
            
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            color = self._get_color_for_id(shape.source_object.id)
            surface.fill(color)
            angle_degrees = -body.angle * 180 / math.pi
            rotated = pygame.transform.rotate(surface, angle_degrees)
            center_x = int(body.position.x * self.pixels_per_mm)
            center_y = int(body.position.y * self.pixels_per_mm)
            rotated_rect = rotated.get_rect(center=(center_x, center_y))
            self._subsurface.blit(rotated, rotated_rect)

        # Масштабируем границы контейнера
        border_width = max(1, int(2 * self.pixels_per_mm / 10))
        container_width = int(self._container.width * self.pixels_per_mm)
        container_height = int(self._container.height * self.pixels_per_mm)
        pygame.draw.rect(self._subsurface, Colors.BLACK, (0, 0, container_width, container_height), border_width)

        return self._subsurface
    
    
    def cleanup(self):
        pass



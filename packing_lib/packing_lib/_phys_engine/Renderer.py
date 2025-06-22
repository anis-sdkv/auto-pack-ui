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
    def get_image_array(self) -> Optional[np.ndarray]:
        pass
    
    @abstractmethod
    def cleanup(self):
        pass


class PygameRenderer(Renderer):
    def __init__(self):
        self._subsurface = None
        self._container = None
    
    def _get_color_for_id(self, obj_id: int) -> Tuple[int, int, int]:
        """Генерирует стабильный цвет для объекта по его ID"""
        rng = random.Random(obj_id)
        return (rng.randint(50, 255), rng.randint(50, 255), rng.randint(50, 255))
        
    def initialize(self, container: PackingContainer) -> Optional[pygame.Surface]:
        self._container = container
        self._subsurface = pygame.Surface((container.width, container.height))
        return self._subsurface
    
    def render(self, rectangles: List, segments: List) -> Optional[pygame.Surface]:
        if not self._subsurface:
            return None
            
        self._subsurface.fill(Colors.WHITE)

        for seg in segments:
            start = int(seg.a.x), int(seg.a.y)
            end = int(seg.b.x), int(seg.b.y)
            pygame.draw.line(self._subsurface, (23, 22, 110), start, end, 3)

        for rect, body, shape in rectangles:
            width = max(1, int(rect.width))
            height = max(1, int(rect.height))
            
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            color = self._get_color_for_id(shape.source_object.id)
            surface.fill(color)
            angle_degrees = -body.angle * 180 / math.pi
            rotated = pygame.transform.rotate(surface, angle_degrees)
            rotated_rect = rotated.get_rect(center=(int(body.position.x), int(body.position.y)))
            self._subsurface.blit(rotated, rotated_rect)

        pygame.draw.rect(self._subsurface, Colors.BLACK, (0, 0, self._container.width, self._container.height), 2)

        return self._subsurface
    
    def get_image_array(self) -> Optional[np.ndarray]:
        if not self._subsurface:
            return None
            
        surf_array = pygame.surfarray.array3d(self._subsurface)
        return np.transpose(surf_array, (1, 0, 2))
    
    def cleanup(self):
        pass


class HeadlessRenderer(Renderer):
    def __init__(self):
        self._container = None
        
    def initialize(self, container: PackingContainer) -> Optional[pygame.Surface]:
        self._container = container
        return None
    
    def render(self, rectangles: List, segments: List) -> Optional[pygame.Surface]:
        return None
    
    def get_image_array(self) -> Optional[np.ndarray]:
        if not self._container:
            return None
        return np.zeros((self._container.height, self._container.width, 3), dtype=np.uint8)
    
    def cleanup(self):
        pass
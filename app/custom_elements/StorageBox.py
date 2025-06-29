import pygame
from typing import List, Dict, Tuple

from app.common import Colors
from packing_lib.packing_lib.types import PlacedObject


class StorageBox:
    def __init__(self, box_real_w, box_real_h):
        self.box_real_w = box_real_w  # мм
        self.box_real_h = box_real_h  # мм
        self.aspect_ratio = box_real_h / box_real_w

        self.fill_color = Colors.WHITE
        self.border_color = Colors.BLACK
        self.border_width = 2

        self.placeables: List[PlacedObject] = []
        self.object_colors: Dict[int, Tuple[int, int, int]] = {}
        self.scale_mm_to_px = 1.0  # масштаб мм -> пиксели

    def update_rect(self, rect: pygame.Rect):
        self.rect = rect
        self.subsurface = pygame.Surface(rect.size)
        self._update_scale()

    def draw(self, surface: pygame.Surface):
        surface.blit(self._render(), self.rect.topleft)

    def set_objects(self, objects: List[PlacedObject]):
        """Устанавливает объекты для отображения"""
        self.placeables = objects

        # Генерируем цвета для новых объектов
        for obj in objects:
            if obj.id not in self.object_colors:
                self.object_colors[obj.id] = self._generate_color(obj.id)

        self._update_scale()
    
    def _generate_color(self, obj_id: int) -> Tuple[int, int, int]:
        """Генерирует детерминированный цвет для объекта по ID"""
        import random
        random.seed(obj_id)
        return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    
    def _update_scale(self):
        """Обновляет масштаб для преобразования мм в пиксели"""
        if hasattr(self, 'rect'):
            # Учитываем границы
            usable_width = self.rect.width - 2 * self.border_width
            usable_height = self.rect.height - 2 * self.border_width
            
            scale_x = usable_width / self.box_real_w
            scale_y = usable_height / self.box_real_h
            self.scale_mm_to_px = min(scale_x, scale_y)
    
    def _render(self):
        self.subsurface.fill(self.fill_color)
        
        for obj in self.placeables:
            # Преобразуем мм в пиксели
            px_width = obj.width * self.scale_mm_to_px
            px_height = obj.height * self.scale_mm_to_px
            px_x = obj.left * self.scale_mm_to_px + self.border_width
            px_y = obj.top * self.scale_mm_to_px + self.border_width
            

            # Проверяем, что объект имеет видимый размер
            if px_width > 0 and px_height > 0:
                rect = pygame.Rect(int(px_x), int(px_y), int(px_width), int(px_height))
                color = self.object_colors.get(obj.id, (128, 128, 128))
                
                pygame.draw.rect(self.subsurface, color, rect)
                pygame.draw.rect(self.subsurface, Colors.BLACK, rect, 1)
            else:
                print(f"    ПРЕДУПРЕЖДЕНИЕ: Объект {obj.id} имеет нулевой размер в пикселях!")

        pygame.draw.rect(self.subsurface, self.border_color, (0, 0, self.rect.width, self.rect.height), self.border_width)
        return self.subsurface

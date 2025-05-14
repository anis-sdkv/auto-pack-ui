import pygame
from app.common import Colors
from app.custom_elements.DrawableRect import DrawableRect
from typing import List


class StorageBox():
    def __init__(self, rect: pygame.Rect):
        self.rect = rect

        self.fill_color = Colors.WHITE
        self.border_color = Colors.BLACK
        self.border_width = 2

        self.placeables: List[DrawableRect] = []

    def draw(self, surface: pygame.Surface):
        surface.fill(self.fill_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)

        for item in self.placeables:
            sprite = pygame.surfarray.make_surface(item.image)
            surface.blit(sprite, (item.x, item.y))

            # self.surface.fill(item.color, item_rect)

    def clear(self):
        self.placeables = []

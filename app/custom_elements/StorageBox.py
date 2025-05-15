import pygame
from pygame.display import update
from pygame.examples.testsprite import update_rects

from app.common import Colors
from app.custom_elements.DrawableRect import DrawableRect
from typing import List


class StorageBox:
    def __init__(self, box_real_w, box_real_h):
        self.aspect_ratio =  box_real_h / box_real_w

        self.fill_color = Colors.WHITE
        self.border_color = Colors.BLACK
        self.border_width = 2

        self.placeables: List[DrawableRect] = []

    def update_rect(self, rect: pygame.Rect):
        self.rect = rect
        self.subsurface = pygame.Surface(rect.size)

    def draw(self, surface: pygame.Surface):
        surface.blit(self._render(), self.rect.topleft)

    def _render(self):
        self.subsurface.fill(self.fill_color)

        for item in self.placeables:
            if item.image is not None:
                sprite = pygame.surfarray.make_surface(item.image)
                self.subsurface.blit(sprite, item.rect.topleft)
            else:
                self.subsurface.fill(item.back_color, item.rect)

        pygame.draw.rect(self.subsurface, self.border_color, (0, 0, self.rect.w, self.rect.h), self.border_width)
        return self.subsurface
        # self.subsurface.fill(self.fill_color)
        # if self.camera_frame is not None:
        #     self._draw_camera_frame()
        # else:
        #     self._draw_generated_boxes()
        # pygame.draw.rect(self.subsurface, self.border_color, (0, 0, self.rect.w, self.rect.h), self.border_width)
        # return self.subsurface

import copy
from pygame_gui import elements

from app.common import Colors
from app.screens.base.ScreenBase import ScreenBase
from packing_lib.packing_lib._phys_engine.PhysicsEngine import PhysicsEngine
import pygame
import math


class PhysScreen(ScreenBase):
    def __init__(self, context, width, height, rects):
        super().__init__(context)

        self.scale_factor = 1000
        self.scaled_width = width * self.scale_factor
        self.scaled_height = height * self.scale_factor
        self.subsurface = pygame.Surface((self.scaled_width, context.surface.get_height()))

        self.storage = pygame.Rect(0, context.surface.get_height() - self.scaled_height, self.scaled_width,
                                   self.scaled_height)

        self.engine = PhysicsEngine(self.storage)
        self.engine.add_rects(rects)

        self.placed_rects = []

        self.back_button = elements.UIButton(
            relative_rect=pygame.Rect((0, 0), (100, 40)),
            text='Назад',
            manager=self.ui_manager)

    def update(self, dt):
        self.engine.update(dt)
        self.placed_rects = []
        for rect, body, shape in self.engine.get_drawable_objects():
            surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            angle_degrees = -body.angle * 180 / math.pi
            rotated = pygame.transform.rotate(surface, angle_degrees)
            rotated_rect = rotated.get_rect(center=(int(body.position.x), int(body.position.y)))

            new_rect = copy.deepcopy(shape.source_object)
            new_rect.rect = rotated_rect
            self.placed_rects.append(new_rect)

    def draw(self):
        self.surface.fill(Colors.WHITE)
        self.surface.blit(self._render(), (self.surface.width / 2 - self.scaled_width / 2, 0))

    def _render(self):
        self.subsurface.fill(Colors.WHITE)

        for seg in self.engine.get_segments():
            start = int(seg.a.x), int(seg.a.y)
            end = int(seg.b.x), int(seg.b.y)
            pygame.draw.line(self.subsurface, (23, 22, 110), start, end, 3)

        for rect, body, shape in self.engine.get_drawable_objects():
            surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            surface.fill(shape.source_object.back_color)
            angle_degrees = -body.angle * 180 / math.pi
            rotated = pygame.transform.rotate(surface, angle_degrees)
            rotated_rect = rotated.get_rect(center=(int(body.position.x), int(body.position.y)))
            self.subsurface.blit(rotated, rotated_rect)

        pygame.draw.rect(self.subsurface, Colors.RED, self.storage, width=2)

        return self.subsurface

    def handle_event(self, event):
        from app.screens.MainScreen import MainScreen
        if event.ui_element == self.back_button:
            self.screen_manager.switch_to(MainScreen)
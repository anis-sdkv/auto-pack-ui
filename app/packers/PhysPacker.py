import pygame
import pymunk
from pymunk.pygame_util import DrawOptions


class PhysPacker:
    def __init__(self, screen_model):
        self.screen_model = screen_model
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)  # Гравитация вниз

        self.bin_width = self.screen_model.storage_box.width
        self.bin_height = self.screen_model.storage_box.height

        self.storage_x = self.screen_model.storage_box.x
        self.storage_y = self.screen_model.storage_box.y

        self._add_walls()

    def _add_walls(self):
        """Добавляем невидимые стены вокруг коробки"""
        walls = [
            pymunk.Segment(self.space.static_body, (self.storage_x, self.storage_y),
                           (self.storage_x, self.storage_y + self.bin_height), 1),  # левая
            pymunk.Segment(self.space.static_body, (self.storage_x + self.bin_width, self.storage_y),
                           (self.storage_x + self.bin_width, self.storage_y + self.bin_height), 1),  # правая
            pymunk.Segment(self.space.static_body, (self.storage_x, self.storage_y + self.bin_height),
                           (self.storage_x + self.bin_width, self.storage_y + self.bin_height), 1),  # дно
        ]
        for wall in walls:
            wall.elasticity = 0.0
            wall.friction = 1.0
            self.space.add(wall)

    def _create_body_for_rect(self, rect):
        """Создаёт pymunk тело и фигуру для прямоугольника"""
        mass = 1
        moment = pymunk.moment_for_box(mass, (rect.width, rect.height))
        body = pymunk.Body(mass, moment)
        body.position = (rect.x, rect.y)
        shape = pymunk.Poly.create_box(body, (rect.width, rect.height))
        shape.friction = 0.8
        shape.elasticity = 0.2
        shape.color = rect.back_color
        shape.original_rect = rect  # сохраним ссылку на исходный прямоугольник
        self.space.add(body, shape)

    def visualize(self, duration=3000):
        """Визуализирует процесс упаковки с физикой в новом окне"""

        pygame.display.set_caption("Physics Packing Visualization")
        width, height = self.bin_width + 100, self.bin_height + 100

        self.screen_model.surface = physics_surface  # перенаправляем отрисовку
        draw_options = DrawOptions(physics_surface)

        # Центруем смещение, чтобы коробка была не впритык
        offset_x = (width - self.bin_width) // 2
        offset_y = (height - self.bin_height) // 2

        self.storage_x += offset_x
        self.storage_y += offset_y

        self._add_walls()

        for rect in self.screen_model.workspace.detected_boxes:
            rect.x += offset_x
            rect.y += offset_y
            self._create_body_for_rect(rect)

        clock = pygame.time.Clock()
        elapsed = 0

        while elapsed < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            self.space.step(1 / 60.0)

            for shape in self.space.shapes:
                if hasattr(shape, "original_rect"):
                    rect = shape.original_rect
                    rect.x = shape.body.position.x
                    rect.y = shape.body.position.y

            physics_surface.fill((30, 30, 30))  # тёмный фон
            self.screen_model.draw()
            self.space.debug_draw(draw_options)
            pygame.display.flip()

            dt = clock.tick(60)
            elapsed += dt

        # Возврат объектов в placeables
        self.screen_model.storage_box.detected_boxes.extend(self.screen_model.workspace.detected_boxes)
        self.screen_model.workspace.detected_boxes = []

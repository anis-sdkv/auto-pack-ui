import copy
from pygame_gui import elements

from app.common import Colors
from app.screens.base.ScreenBase import ScreenBase
from app.physics.PhysicsEngine import PhysicsEngine
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

        self.engine = PhysicsEngine(self.storage, self, 10)
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
        for x, y, w, h in self.engine.empty_areas:
            pygame.draw.rect(self.surface, (255, 0, 0), (self.surface.width / 2 - self.scaled_width / 2 + x, y, w, h), 2)

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

# import copy
# import math
#
# import pygame
# import pymunk
# from pygame import Rect
# import random
#
# from app.common import Colors
# from app.screens.base.ScreenBase import ScreenBase
#
#
# class PhysScreen(ScreenBase):
#     def __init__(self, context, width, height, rects):
#         super().__init__(context)
#
#         self.space = pymunk.Space()  # Создаем физическое пространство
#         self.space.gravity = (0, 1000)  # Гравитация (падение объектов вниз)
#         self.space.cell_size = 1
#         self.space.collision_slop = 0.5  # Стандартное значение
#         self.space.collision_bias = 0.1  # Стандартное значение
#         self.space.iterations = 30  # Можно уменьшить обратно
#         self.space.damping = 0.9
#         self.collision_handler = self.space.add_default_collision_handler()
#         self.collision_handler.begin = self.on_collision_begin
#         # self.collision_handler.pre_solve = self.on_pre_solve  # Добавим обработчик pre-solve
#
#         self.scale_factor = 100
#
#         self.storage = Rect(0, self.context.surface.height - context.config.box_height,
#                             context.config.box_width * self.scale_factor, context.config.box_height * self.scale_factor)
#         self.create_boundaries(self.storage)
#
#         self.rectangles = []
#         self.create_phys_for_rects(rects)
#         self.shake_timer = 10  # секунды
#
#     def on_collision_begin(self, arbiter, space, data):
#         # Этот метод вызывается при начале столкновения
#         # Можно добавить логику для предотвращения проникновения
#         return True  # True означает, что столкновение разрешено
#
#     def create_boundaries(self, storage: Rect):
#         static_body = self.space.static_body
#         self.space.add(
#             pymunk.Segment(static_body, (storage.x, storage.height), (storage.width, storage.height), 0),
#             pymunk.Segment(static_body, (storage.x, storage.y), (storage.x, storage.height), 0),
#             pymunk.Segment(static_body, (storage.width, storage.y), (storage.width, storage.height), 0),
#         )
#
#     def create_phys_for_rects(self, rects):
#         rects = sorted(rects, key=lambda x: x.width * x.height, reverse=True)
#         y_counter = self.storage.y
#         for rect in rects:
#             rect.x = self.storage.width / 2 - rect.width / 2
#             rect.y = y_counter
#             y_counter -= rect.height - 10
#
#             # Физическое тело для прямоугольника
#             mass = 0.1
#             inertia = pymunk.moment_for_box(mass, (rect.width, rect.height))
#             body = pymunk.Body(mass, inertia)
#             body.position = (rect.x + rect.width / 2, rect.y + rect.height / 2)
#             # Запрещаем вращение тела
#             # body.moment = float('inf')  # Бесконечный момент инерции предотвращает вращение
#
#             shape = pymunk.Poly.create_box(body, (rect.width, rect.height))
#             shape.friction = 1
#             shape.elasticity = 0
#             shape.color = rect.back_color
#             self.space.add(body, shape)
#
#             # Добавляем в список прямоугольников
#             self.rectangles.append((rect, body, shape))
#
#     def update(self, dt):
#         if self.shake_timer > 0:
#             if self.shake_timer < 2:
#                 PhysScreen.shake_space_randomly(self.space, strength=10)
#             else:
#                 PhysScreen.shake_space_randomly(self.space, strength=5)
#             self.shake_timer -= dt
#
#         self.space.step(dt)
#
#     def draw(self):
#         self.surface.fill(Colors.WHITE)
#
#         for shape in self.space.shapes:
#             if isinstance(shape, pymunk.Segment):
#                 start = int(shape.a.x), int(shape.a.y)
#                 end = int(shape.b.x), int(shape.b.y)
#                 pygame.draw.line(self.surface, (23, 22, 110), start, end, 3)
#
#         # Отображаем физику (прямоугольники)
#         # old без поворотов
#         # for rect, body, shape in self.rectangles:
#         #     pygame.draw.rect(self.surface, shape.color,
#         #                      Rect(body.position.x - rect.width / 2, body.position.y - rect.height / 2,
#         #                           rect.width, rect.height))
#         #     print(body.angle)
#
#         for rect, body, shape in self.rectangles:
#             # Создаем поверхность для прямоугольника
#             rect_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
#
#             # Заполняем поверхность цветом прямоугольника
#             rect_surface.fill(shape.back_color)
#
#             # Поворачиваем поверхность на угол тела
#             angle_degrees = -body.angle * 180 / math.pi  # Преобразуем радианы в градусы
#             rotated_surface = pygame.transform.rotate(rect_surface, angle_degrees)
#
#             # Получаем новые размеры повернутой поверхности
#             rotated_rect = rotated_surface.get_rect()
#
#             # Размещаем повернутый прямоугольник в позиции тела
#             rotated_rect.center = (int(body.position.x), int(body.position.y))
#
#             # Отрисовываем повернутую поверхность
#             self.surface.blit(rotated_surface, rotated_rect)
#
#         self.context.ui_manager.draw_ui(self.surface)
#         pygame.display.flip()
#
#     def handle_event(self, event):
#         pass
#
#     @staticmethod
#     def shake_space_randomly(space, strength=10000):
#         for body in space.bodies:
#             if body.body_type == pymunk.Body.DYNAMIC:
#                 # Генерируем случайные силы для X и Y
#                 dx = random.uniform(-strength, strength)
#                 dy = random.uniform(-strength, strength)
#
#                 # Применяем импульс на тело
#                 body.apply_impulse_at_local_point((dx, dy))

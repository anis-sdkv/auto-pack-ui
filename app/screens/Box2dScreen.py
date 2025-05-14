# import pygame
# import random
# from Box2D.b2 import (world, polygonShape, dynamicBody)
# from pygame import Color, Rect
#
# from app.common import Colors
# from app.screens.base.ScreenBase import ScreenBase
# import math
#
#
# class Box2dScreen(ScreenBase):
#     def __init__(self, context, main_screen_model):
#         super().__init__(context)
#         self.context = context
#
#         # Создаем физическое пространство (мир Box2D)
#         self.world = world(gravity=(0, -10), doSleep=True)
#
#         self.timeStep = 1.0 / 60
#         self.vel_iters = 6
#         self.pos_iters = 2
#
#         self.storage = Rect(0, context.surface.height - main_screen_model.storage_box.height,
#                             main_screen_model.storage_box.width, main_screen_model.storage_box.height)
#
#         self.create_boundaries(self.storage)
#
#         self.rectangles = []
#         self.create_phys_for_rects(main_screen_model.workspace.placeables)
#
#         self.shake_timer = 10  # секунды
#
#     def create_boundaries(self, storage: Rect):
#         # Создаём 3 статических стены (низ, левая, правая)
#         wall_thickness = 5  # Толщина стен (в метрах / 10)
#
#         # Пол (нижняя горизонтальная стена)
#         floor = self.world.CreateStaticBody(
#             position=(0, (storage.height - wall_thickness) / 10),
#             shapes=polygonShape(box=(storage.width / 20, wall_thickness / 2))
#         )
#
#         # Левая стенка (вертикальная)
#         left_wall = self.world.CreateStaticBody(
#             position=(wall_thickness / 2 / 10, (storage.y + storage.height / 2) / 10),
#             shapes=polygonShape(box=(wall_thickness / 2, storage.height / 20))
#         )
#
#         # Правая стенка (вертикальная)
#         right_wall = self.world.CreateStaticBody(
#             position=((storage.width - wall_thickness / 2) / 10, (storage.y + storage.height / 2) / 10),
#             shapes=polygonShape(box=(wall_thickness / 2, storage.height / 20))
#         )
#
#         # Сохраняем для отрисовки
#         self.boundaries = [floor, left_wall, right_wall]
#
#     def create_phys_for_rects(self, rects):
#         rects = sorted(rects, key=lambda x: x.width * x.height, reverse=True)
#
#         for rect in rects:
#             body = self.world.CreateDynamicBody(
#                 position=((rect.x + rect.width / 2) / 10, (rect.y + rect.height / 2) / 10),
#                 angle=0
#             )
#             box = body.CreatePolygonFixture(box=(rect.width / 20, rect.height / 20), density=1, friction=0.5)
#             self.rectangles.append((rect, body))
#
#     def update(self, dt):
#         if self.shake_timer > 0:
#             if self.shake_timer < 2:
#                 Box2dScreen.shake_space_randomly(self.world, strength=50)
#             else:
#                 Box2dScreen.shake_space_randomly(self.world, strength=20)
#             self.shake_timer -= dt
#
#         self.world.Step(self.timeStep, self.vel_iters, self.pos_iters)
#
#     def draw(self):
#         self.surface.fill(Colors.WHITE)
#
#         # Отрисовка объектов
#         for rect, body in self.rectangles:
#             position = body.position
#             angle = body.angle
#
#             center_x = position.x * 10
#             center_y = self.context.surface.get_height() - position.y * 10  # инверсия Y
#             width = rect.width
#             height = rect.height
#
#             points = [
#                 (-width/2, -height/2),
#                 (width/2, -height/2),
#                 (width/2, height/2),
#                 (-width/2, height/2)
#             ]
#
#             rotated_points = []
#             for x, y in points:
#                 rotated_x = x * math.cos(angle) - y * math.sin(angle)
#                 rotated_y = x * math.sin(angle) + y * math.cos(angle)
#                 rotated_points.append((center_x + rotated_x, center_y + rotated_y))
#
#             pygame.draw.polygon(self.surface, Color("blue"), rotated_points)
#
#         self.context.ui_manager.draw_ui(self.surface)
#         pygame.display.flip()
#
#     def handle_event(self, event):
#         pass
#
#     @staticmethod
#     def shake_space_randomly(world, strength=10):
#         for body in world.bodies:
#             if body.type == dynamicBody:
#                 dx = random.uniform(-strength, strength)
#                 dy = random.uniform(-strength, strength)
#                 body.ApplyLinearImpulse((dx, dy), body.worldCenter, True)

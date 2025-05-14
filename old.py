# import pygame
# import random
# import sys
# from typing import List, Tuple
# import time
#
# # Константы
# SCREEN_WIDTH = 1200
# SCREEN_HEIGHT = 700
# LEFT_PANEL_WIDTH = SCREEN_WIDTH // 2
# BACKGROUND_COLOR = (240, 240, 240)
# BORDER_COLOR = (0, 0, 0)
# BOX_COLOR = (220, 220, 220)
# RECTANGLE_COLORS = [
#     (255, 102, 102),  # красный
#     (102, 178, 255),  # синий
#     (102, 255, 102),  # зеленый
#     (255, 178, 102),  # оранжевый
#     (178, 102, 255),  # фиолетовый
#     (255, 255, 102),  # желтый
#     (102, 255, 178),  # бирюзовый
#     (255, 102, 178),  # розовый
# ]
#
#
# # Модель
# class Rectangle:
#     def __init__(self, width: int, height: int, color: Tuple[int, int, int]):
#         self.width = width
#         self.height = height
#         self.color = color
#         self.x = 0
#         self.y = 0
#         self.is_placed = False
#
#     def set_position(self, x: int, y: int):
#         self.x = x
#         self.y = y
#
#     def contains_point(self, point_x: int, point_y: int) -> bool:
#         return (self.x <= point_x <= self.x + self.width and
#                 self.y <= point_y <= self.y + self.height)
#
#
# class Box:
#     def __init__(self, width: int, height: int):
#         self.width = width
#         self.height = height
#         self.x = LEFT_PANEL_WIDTH + 50
#         self.y = 50
#         self.rectangles = []
#         # Для алгоритма упаковки
#         self.spaces = [(0, 0, width, height)]  # (x, y, width, height)
#
#     def add_rectangle(self, rectangle: Rectangle) -> bool:
#         # Обновляем позицию прямоугольника и добавляем в коробку
#         for i, (space_x, space_y, space_w, space_h) in enumerate(self.spaces):
#             if rectangle.width <= space_w and rectangle.height <= space_h:
#                 # Прямоугольник помещается в текущее пространство
#                 rectangle.set_position(self.x + space_x, self.y + space_y)
#                 self.rectangles.append(rectangle)
#
#                 # Удаляем использованное пространство
#                 self.spaces.pop(i)
#
#                 # Создаем новые пространства (справа и снизу от размещенного прямоугольника)
#                 if space_w - rectangle.width > 0:  # Справа
#                     self.spaces.append(
#                         (space_x + rectangle.width, space_y, space_w - rectangle.width, rectangle.height))
#                 if space_h - rectangle.height > 0:  # Снизу
#                     self.spaces.append((space_x, space_y + rectangle.height, space_w, space_h - rectangle.height))
#
#                 # Сортируем пространства по площади (сначала меньшие)
#                 self.spaces.sort(key=lambda s: s[2] * s[3])
#
#                 return True
#
#         return False
#
#     def clear(self):
#         """Очистить коробку от всех прямоугольников и сбросить свободные пространства"""
#         self.rectangles = []
#         self.spaces = [(0, 0, self.width, self.height)]
#
#
# class WorkspaceModel:
#     def __init__(self):
#         self.rectangles = []
#         self.box = Box(SCREEN_WIDTH // 3, SCREEN_HEIGHT - 100)
#         self.dragged_rectangle = None
#
#     def create_random_rectangles(self, count: int):
#         # Сначала сохраняем упакованные прямоугольники
#         placed_rectangles = [r for r in self.rectangles if r.is_placed]
#
#         # Создаем новый список с неупакованными прямоугольниками
#         self.rectangles = []
#         for _ in range(count):
#             width = random.randint(30, 100)
#             height = random.randint(30, 100)
#             color = random.choice(RECTANGLE_COLORS)
#             rect = Rectangle(width, height, color)
#             # Размещаем прямоугольники на левой панели
#             rect.set_position(
#                 random.randint(50, LEFT_PANEL_WIDTH - 150),
#                 random.randint(50, SCREEN_HEIGHT - 150)
#             )
#             self.rectangles.append(rect)
#
#         # Добавляем обратно упакованные прямоугольники
#         self.rectangles.extend(placed_rectangles)
#
#     def reset_all(self):
#         """Полностью сбросить рабочее пространство и коробку"""
#         self.rectangles = []
#         self.box.clear()
#         self.dragged_rectangle = None
#         self.create_random_rectangles(8)
#
#     def get_rectangle_at_position(self, x: int, y: int) -> Rectangle:
#         # Проверяем с конца списка, чтобы выбрать верхний прямоугольник
#         for rect in reversed(self.rectangles):
#             if not rect.is_placed and rect.contains_point(x, y):
#                 return rect
#         return None
#
#     def start_drag(self, x: int, y: int) -> bool:
#         self.dragged_rectangle = self.get_rectangle_at_position(x, y)
#         return self.dragged_rectangle is not None
#
#     def update_drag_position(self, x: int, y: int):
#         if self.dragged_rectangle:
#             self.dragged_rectangle.set_position(
#                 x - self.dragged_rectangle.width // 2,
#                 y - self.dragged_rectangle.height // 2
#             )
#
#     def end_drag(self, x: int, y: int) -> bool:
#         if not self.dragged_rectangle:
#             return False
#
#         # Проверяем, попал ли прямоугольник в коробку
#         box_rect = pygame.Rect(
#             self.box.x, self.box.y,
#             self.box.width, self.box.height
#         )
#         drag_rect = pygame.Rect(
#             self.dragged_rectangle.x, self.dragged_rectangle.y,
#             self.dragged_rectangle.width, self.dragged_rectangle.height
#         )
#
#         if box_rect.colliderect(drag_rect):
#             # Пытаемся добавить прямоугольник в коробку с помощью алгоритма упаковки
#             if self.box.add_rectangle(self.dragged_rectangle):
#                 self.dragged_rectangle.is_placed = True
#                 self.dragged_rectangle = None
#                 return True
#
#         # Если не удалось добавить, возвращаем прямоугольник на рабочее пространство
#         self.dragged_rectangle = None
#         return False
#
#     def pack_all_rectangles(self):
#         # Сортировка прямоугольников по убыванию площади для лучшей упаковки
#         unplaced_rectangles = [r for r in self.rectangles if not r.is_placed]
#         unplaced_rectangles.sort(key=lambda r: r.width * r.height, reverse=True)
#
#         # Возвращаем неразмещенные прямоугольники для визуализации пошаговой упаковки
#         return unplaced_rectangles
#
#
# # View
# class WorkspaceView:
#     def __init__(self, model: WorkspaceModel):
#         self.model = model
#         self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#         pygame.display.set_caption("Алгоритм оптимальной упаковки")
#         self.font = pygame.font.SysFont(None, 18)
#         self.clock = pygame.time.Clock()
#
#     def draw(self):
#         # Очистка экрана
#         self.screen.fill(BACKGROUND_COLOR)
#
#         # Рисуем разделитель
#         pygame.draw.line(
#             self.screen,
#             BORDER_COLOR,
#             (LEFT_PANEL_WIDTH, 0),
#             (LEFT_PANEL_WIDTH, SCREEN_HEIGHT),
#             3
#         )
#
#         # Рисуем коробку
#         box = self.model.box
#         pygame.draw.rect(
#             self.screen,
#             BOX_COLOR,
#             (box.x, box.y, box.width, box.height)
#         )
#         pygame.draw.rect(
#             self.screen,
#             BORDER_COLOR,
#             (box.x, box.y, box.width, box.height),
#             2
#         )
#
#         # Рисуем прямоугольники
#         for rect in self.model.rectangles:
#             pygame.draw.rect(
#                 self.screen,
#                 rect.color,
#                 (rect.x, rect.y, rect.width, rect.height)
#             )
#             pygame.draw.rect(
#                 self.screen,
#                 BORDER_COLOR,
#                 (rect.x, rect.y, rect.width, rect.height),
#                 2
#             )
#
#             # Добавляем размеры на прямоугольник
#             size_text = self.font.render(f"{rect.width}x{rect.height}", True, (0, 0, 0))
#             text_x = rect.x + (rect.width - size_text.get_width()) // 2
#             text_y = rect.y + (rect.height - size_text.get_height()) // 2
#             self.screen.blit(size_text, (text_x, text_y))
#
#         # Рисуем кнопку "Pack All"
#         pack_button = pygame.Rect(50, SCREEN_HEIGHT - 60, 120, 40)
#         pygame.draw.rect(self.screen, (150, 150, 150), pack_button)
#         pygame.draw.rect(self.screen, BORDER_COLOR, pack_button, 2)
#         pack_text = self.font.render("Pack All", True, (0, 0, 0))
#         self.screen.blit(
#             pack_text,
#             (pack_button.x + (pack_button.width - pack_text.get_width()) // 2,
#              pack_button.y + (pack_button.height - pack_text.get_height()) // 2)
#         )
#
#         # Рисуем кнопку "New Rectangles"
#         new_button = pygame.Rect(200, SCREEN_HEIGHT - 60, 160, 40)
#         pygame.draw.rect(self.screen, (150, 150, 150), new_button)
#         pygame.draw.rect(self.screen, BORDER_COLOR, new_button, 2)
#         new_text = self.font.render("New Rectangles", True, (0, 0, 0))
#         self.screen.blit(
#             new_text,
#             (new_button.x + (new_button.width - new_text.get_width()) // 2,
#              new_button.y + (new_button.height - new_text.get_height()) // 2)
#         )
#
#         # Рисуем кнопку "Reset All"
#         reset_button = pygame.Rect(380, SCREEN_HEIGHT - 60, 120, 40)
#         pygame.draw.rect(self.screen, (255, 150, 150), reset_button)
#         pygame.draw.rect(self.screen, BORDER_COLOR, reset_button, 2)
#         reset_text = self.font.render("Reset All", True, (0, 0, 0))
#         self.screen.blit(
#             reset_text,
#             (reset_button.x + (reset_button.width - reset_text.get_width()) // 2,
#              reset_button.y + (reset_button.height - reset_text.get_height()) // 2)
#         )
#
#         # Рисуем информацию о количестве прямоугольников
#         unplaced_count = len([r for r in self.model.rectangles if not r.is_placed])
#         placed_count = len([r for r in self.model.rectangles if r.is_placed])
#
#         info_text = self.font.render(
#             f"Неупакованные: {unplaced_count} | Упакованные: {placed_count}",
#             True,
#             (0, 0, 0)
#         )
#         self.screen.blit(info_text, (50, SCREEN_HEIGHT - 100))
#
#         pygame.display.flip()
#
#         return pack_button, new_button, reset_button
#
#     def animate_pack_all(self, rectangles_to_pack: List[Rectangle]):
#         for rect in rectangles_to_pack:
#             # Анимируем перемещение прямоугольника в коробку
#             start_x, start_y = rect.x, rect.y
#
#             # Пытаемся добавить прямоугольник в коробку
#             box = self.model.box
#             if box.add_rectangle(rect):
#                 target_x, target_y = rect.x, rect.y
#                 rect.x, rect.y = start_x, start_y  # Возвращаем на начальное положение для анимации
#
#                 # Анимация движения
#                 steps = 30
#                 for step in range(steps + 1):
#                     rect.x = start_x + (target_x - start_x) * step / steps
#                     rect.y = start_y + (target_y - start_y) * step / steps
#
#                     self.draw()
#                     pygame.time.delay(10)
#
#                 rect.is_placed = True
#             else:
#                 # Если не удалось упаковать, показываем красное свечение
#                 original_color = rect.color
#                 rect.color = (255, 0, 0)
#                 self.draw()
#                 pygame.time.delay(300)
#                 rect.color = original_color
#
#
# # App - связующее звено, теперь обходится без ViewModel
# class App:
#     def __init__(self):
#         pygame.init()
#         self.model = WorkspaceModel()
#         self.view = WorkspaceView(self.model)
#         self.model.create_random_rectangles(8)
#         self.running = True
#         self.clock = pygame.time.Clock()
#
#     def run(self):
#         while self.running:
#             pack_button, new_button, reset_button = self.view.draw()
#             self.clock.tick(60)
#
#             # Обработка событий
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.running = False
#
#                 elif event.type == pygame.MOUSEBUTTONDOWN:
#                     if event.button == 1:  # левая кнопка мыши
#                         x, y = pygame.mouse.get_pos()
#
#                         # Проверяем, нажата ли кнопка "Pack All"
#                         if pack_button.collidepoint(x, y):
#                             rectangles_to_pack = self.model.pack_all_rectangles()
#                             self.view.animate_pack_all(rectangles_to_pack)
#
#                         # Проверяем, нажата ли кнопка "New Rectangles"
#                         elif new_button.collidepoint(x, y):
#                             self.model.create_random_rectangles(8)
#
#                         # Проверяем, нажата ли кнопка "Reset All"
#                         elif reset_button.collidepoint(x, y):
#                             self.model.reset_all()
#
#                         # Иначе пробуем начать перетаскивание прямоугольника
#                         else:
#                             self.model.start_drag(x, y)
#
#                 elif event.type == pygame.MOUSEMOTION:
#                     x, y = pygame.mouse.get_pos()
#                     self.model.update_drag_position(x, y)
#
#                 elif event.type == pygame.MOUSEBUTTONUP:
#                     if event.button == 1:  # левая кнопка мыши
#                         x, y = pygame.mouse.get_pos()
#                         self.model.end_drag(x, y)
#
#         pygame.quit()
#         sys.exit()
#
# if __name__ == "__main__":
#     app = App()
#     app.run()
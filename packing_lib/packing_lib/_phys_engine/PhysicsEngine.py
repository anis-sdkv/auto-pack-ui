from typing import List, Optional

import numpy as np
import pymunk
import random
import math

from packing_lib.packing_lib._phys_engine.BodyTracker import BodyTracker
from packing_lib.packing_lib._phys_engine.EmptyAreaFinder import find_empty_areas
from packing_lib.packing_lib._phys_engine.PhysicsConfig import PhysicsConfig
from packing_lib.packing_lib.types import PackInputObject, PackingContainer, SortOrder


class PhysicsEngine:
    def __init__(self, box_rect: PackingContainer, config: PhysicsConfig = PhysicsConfig(), sort_order: SortOrder = SortOrder.DESCENDING):
        self.config = config
        self.sort_order = sort_order
        self.done = False
        self.speed_multiplier = self.config.simulation_speed_multiplier

        self._box_rect = box_rect

        self._rectangles = []
        self._shake_timer = self.config.shake_duration

        self._rotation_index = 0
        self._rotation_done = False

        self._overlap_index = 0
        self._overlap_rotated = False
        self._resolved_overlaps = False

        self._empty_areas = []
        self._empty_filled = False

        self._stationary_counter = 0
        self._shake_strength = self.config.initial_shake_strength

        self._trackers = None

        self._setup_space()
        self._create_boundaries(box_rect)

    def _setup_space(self):
        self.space = pymunk.Space()
        self.space.gravity = self.config.space_gravity
        self.space.damping = self.config.space_damping
        self.space.iterations = self.config.space_iterations
        self.space.collision_slop = self.config.space_collision_slop

    @staticmethod
    def _on_collision_begin(arbiter, space, data):
        return True

    def _create_boundaries(self, container):
        s = self.space
        b = s.static_body

        points = [
            (0, -self.config.boundary_depth),
            (0, container.height),
            (container.width, container.height),
            (container.width, -self.config.boundary_depth),
        ]

        s.add(
            pymunk.Segment(b, points[0], points[1], 0),
            pymunk.Segment(b, points[1], points[2], 0),
            pymunk.Segment(b, points[2], points[3], 0),
        )

    def add_rects(self, rects: List[PackInputObject]):
        # Сортируем объекты в зависимости от выбранного порядка
        if self.sort_order == SortOrder.DESCENDING:
            rects = sorted(rects, key=lambda x: x.width * x.height, reverse=True)
        elif self.sort_order == SortOrder.ASCENDING:
            rects = sorted(rects, key=lambda x: x.width * x.height, reverse=False)
        elif self.sort_order == SortOrder.RANDOM:
            rects = rects.copy()  # копируем чтобы не изменять исходный список
            random.shuffle(rects)
        y_counter = 0
        for rect in rects:
            x_pos = random.randint(0, int(self._box_rect.width - rect.width))
            y_pos = y_counter
            y_counter -= rect.height - self.config.object_spacing

            inertia = pymunk.moment_for_box(self.config.body_mass, (rect.width, rect.height))
            body = pymunk.Body(self.config.body_mass, inertia)
            body.position = (x_pos + rect.width / 2, y_pos + rect.height / 2)

            shape = pymunk.Poly.create_box(body, (rect.width, rect.height))
            shape.friction = self.config.body_friction
            shape.elasticity = self.config.body_elasticity
            shape.source_object = rect

            self.space.add(body, shape)
            self._rectangles.append((rect, body, shape))

        self._trackers = [BodyTracker(body, self.config.position_threshold, self.config.angle_threshold) for body in
                          self.space.bodies if body.body_type == pymunk.Body.DYNAMIC]

    def get_colliding_pairs(self):
        colliding = []
        shapes = self.space.shapes
        for i in range(len(shapes)):
            for j in range(i + 1, len(shapes)):
                s1, s2 = shapes[i], shapes[j]
                if s1.shapes_collide(s2).points:
                    colliding.append((s1, s2))
        return colliding

    def _collect_objects_for_placement(self):
        """
        Собирает объекты, которые нужно разместить в пустых областях,
        и физически удаляет их из space и списка drawables
        """
        objects_to_place = []
        objects_to_remove_indices = []

        for i, (rect, body, shape) in enumerate(self._rectangles):
            if body.body_type == pymunk.Body.STATIC:
                continue

            # Получаем актуальные размеры объекта с учетом поворота
            actual_width, actual_height = self._get_actual_dimensions(
                rect.width, rect.height, body.angle
            )

            # Проверяем объекты за верхней границей и другими границами
            if (body.position.y - actual_height / 2 < 0 or  # улетели вверх
                    body.position.y - rect.height / 2 > self._box_rect.height or  # упали вниз
                    body.position.x - rect.width / 2 > self._box_rect.width or  # улетели вправо
                    body.position.x + rect.width / 2 < 0):  # улетели влево
                objects_to_place.append((rect, body, shape))
                objects_to_remove_indices.append(i)
                # Физически удаляем из space чтобы освободить место
                self.space.remove(body, shape)

        # Удаляем из списка drawables (в обратном порядке индексов)
        for i in reversed(objects_to_remove_indices):
            del self._rectangles[i]

        return objects_to_place

    def _fill_empty_areas(self, rects_to_place):
        self._empty_areas = find_empty_areas(self.get_image_array())
        for empty_area in self._empty_areas:
            ex, ey, ew, eh = empty_area
            for i, (rect, body, shape) in enumerate(rects_to_place):
                rw, rh = rect.width, rect.height
                can_fit_normal = rw <= ew and rh <= eh
                can_fit_rotated = rh <= ew and rw <= eh

                if can_fit_normal or can_fit_rotated:
                    if not can_fit_normal:
                        body.angle = self.config.rotation_angles_rad[1]  # 90 градусов
                    else:
                        body.angle = self.config.rotation_angles_rad[0]  # 0 градусов

                    rw, rh = rect.width, rect.height
                    body.position = (ex + rw / 2, ey + rh / 2)
                    body.velocity = (0, 0)

                    self.space.add(body, shape)
                    self._rectangles.append((rect, body, shape))
                    del rects_to_place[i]
                    break

        self._empty_filled = True

    def update(self, dt):
        self._update_trackers()

        if self._stationary_counter > self.config.stationary_threshold:
            if not self._rotation_done:
                self._rotate_next_rectangle()
                if self._rotation_index >= len(self._rectangles):
                    self._shake_timer = self.config.shake_duration
                    self._shake_strength = self.config.post_rotation_shake_strength
            elif self._shake_timer < 0 and not self._empty_filled:
                objects_to_place = self._collect_objects_for_placement()
                self._fill_empty_areas(objects_to_place)
                self._shake_timer = self.config.shake_duration

        for _ in range(self.speed_multiplier):
            if self._shake_timer > 0:
                self._shake(strength=self._shake_strength)
                self._shake_timer -= dt
            elif self._empty_filled:
                self.done = True

            self.space.step(dt)

    def _update_trackers(self):
        self.active_trackers = 0
        for tracker in self._trackers:
            if not tracker.is_stationary():
                self.active_trackers += 1
            tracker.update()
        if self.active_trackers == 0:
            self._stationary_counter += 1
        else:
            self._stationary_counter = 0

    def _rotate_next_rectangle(self):
        if self._rotation_index >= len(self._rectangles):
            self._rotation_done = True
            return

        rect, body, shape = self._rectangles[self._rotation_index]

        current_angle = body.angle % (2 * math.pi)

        # Целевые углы из конфигурации
        vertical_angles = self.config.rotation_angles_rad

        # Найти ближайший вертикальный угол
        closest_angle = min(vertical_angles, key=lambda a: abs(a - current_angle))

        body.angle = closest_angle
        body.angular_velocity = 0
        body.moment = float("inf")
        self.space.reindex_shapes_for_body(body)
        self._rotation_index += 1

    def _get_actual_dimensions(self, original_width, original_height, body_angle):
        """
        Вычисляет актуальные размеры объекта с учетом поворота.
        
        Args:
            original_width: исходная ширина
            original_height: исходная высота  
            body_angle: угол поворота body в радианах
            
        Returns:
            tuple: (актуальная_ширина, актуальная_высота)
        """
        # Нормализуем угол к диапазону [0, 2π]
        angle = body_angle % (2 * math.pi)

        # Проверяем близость к вертикальным углам (90° и 270°) с допуском
        tolerance = math.pi / 4  # 45 градусов

        # 90° (π/2) или 270° (3π/2) - вертикальная ориентация
        if (math.pi / 2 - tolerance < angle < math.pi / 2 + tolerance or
                3 * math.pi / 2 - tolerance < angle < 3 * math.pi / 2 + tolerance):
            return original_height, original_width
        else:
            # 0° или 180° - горизонтальная ориентация
            return original_width, original_height

    def _shake(self, strength=None):
        if strength is None:
            strength = self.config.default_shake_force
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                dx = random.uniform(-strength, strength)
                dy = random.uniform(-strength, strength)
                body.apply_impulse_at_local_point((dx, dy), (0, 0))

    def get_drawable_objects(self):
        return self._rectangles

    def get_segments(self):
        return [s for s in self.space.shapes if isinstance(s, pymunk.Segment)]

    def get_image_array(self):
        """Создает numpy массив с текущим состоянием объектов для анализа пустых областей"""
        width = int(self._box_rect.width )
        height = int(self._box_rect.height )

        # Создаем белый фон
        image_array = np.full((height, width, 3), 255, dtype=np.uint8)

        # Рисуем границы контейнера (черные линии)
        image_array[0, :] = 0  # верхняя граница
        image_array[-1, :] = 0  # нижняя граница
        image_array[:, 0] = 0  # левая граница
        image_array[:, -1] = 0  # правая граница

        # Рисуем все объекты
        for rect, body, shape in self._rectangles:
            if body.body_type == pymunk.Body.STATIC:
                continue
            self._draw_rectangle_to_array(image_array, rect, body)

        return image_array

    def _draw_rectangle_to_array(self, image_array, rect, body):
        """Рисует прямоугольник в numpy массиве с учетом поворота"""
        # Получаем размеры и позицию с масштабированием
        width = rect.width
        height = rect.height
        center_x = body.position.x
        center_y = body.position.y
        angle = body.angle

        # Вычисляем углы прямоугольника с учетом поворота
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        hw, hh = width / 2, height / 2

        # Углы прямоугольника относительно центра
        corners = [
            (-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)
        ]

        # Поворачиваем углы и переводим в абсолютные координаты
        rotated_corners = []
        for x, y in corners:
            rx = x * cos_a - y * sin_a + center_x
            ry = x * sin_a + y * cos_a + center_y
            rotated_corners.append((int(rx), int(ry)))

        # Заполняем область прямоугольника
        self._fill_polygon_in_array(image_array, rotated_corners)

    def _fill_polygon_in_array(self, image_array, corners):
        """Заполняет многоугольник в numpy массиве"""
        if len(corners) < 3:
            return

        # Находим границы (используем размеры массива)
        height, width = image_array.shape[:2]
        min_y = max(0, min(y for x, y in corners))
        max_y = min(height - 1, max(y for x, y in corners))

        # Для каждой строки находим пересечения с гранями многоугольника
        for y in range(min_y, max_y + 1):
            intersections = []

            # Проверяем пересечения с каждой гранью
            for i in range(len(corners)):
                x1, y1 = corners[i]
                x2, y2 = corners[(i + 1) % len(corners)]

                if y1 != y2:  # Исключаем горизонтальные линии
                    if min(y1, y2) <= y <= max(y1, y2):
                        # Вычисляем x-координату пересечения
                        x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                        intersections.append(int(x))

            # Сортируем пересечения и заполняем отрезки
            intersections.sort()
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    x_start = max(0, intersections[i])
                    x_end = min(width - 1, intersections[i + 1])
                    if x_start <= x_end:
                        image_array[y, x_start:x_end + 1] = 0  # Черный цвет


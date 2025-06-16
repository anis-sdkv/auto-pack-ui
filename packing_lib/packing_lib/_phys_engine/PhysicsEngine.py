from typing import List

import numpy as np
import pymunk
import random
import math

import pygame

from app.common import Colors
from packing_lib.packing_lib._phys_engine.BodyTracker import BodyTracker
from packing_lib.packing_lib._phys_engine.EmptyAreaFinder import find_empty_areas
from packing_lib.packing_lib._phys_engine.PhysicsConfig import PhysicsConfig
from packing_lib.packing_lib.types import RectObject, Container


class PhysicsEngine:
    def __init__(self, box_rect: Container, config: PhysicsConfig = PhysicsConfig()):
        self.config = config
        self.done = False
        self.speed_multiplier = self.config.simulation_speed_multiplier
        self._subsurface = pygame.Surface((box_rect.width, box_rect.height))

        self._box_rect = box_rect

        self._rectangles = []
        self._shake_timer = 4

        self._rotation_index = 0
        self._rotation_done = False

        self._overlap_index = 0
        self._overlap_rotated = False
        self._resolved_overlaps = False

        self._empty_areas = []
        self._empty_filled = False

        self._stationary_counter = 0
        self._shake_strength = 10

        self._trackers = None

        self._setup_space()
        self._create_boundaries(box_rect)

    def _setup_space(self):
        self.space = pymunk.Space()
        self.space.gravity = self.config.space_gravity
        self.space.damping = self.config.space_damping
        self.space.iterations = self.config.space_iterations
        self.space.collision_slop = self.config.space_collision_slop
        self._setup_collision_handler()

    def _setup_collision_handler(self):
        self.collision_handler = self.space.add_default_collision_handler()
        self.collision_handler.begin = self._on_collision_begin

    @staticmethod
    def _on_collision_begin(arbiter, space, data):
        return True

    def _create_boundaries(self, container):
        s = self.space
        b = s.static_body

        points = [
            (0, -10000),
            (0, container.height),
            (container.width, container.height),
            (container.width, -10000),
        ]

        s.add(
            pymunk.Segment(b, points[0], points[1], 0),
            pymunk.Segment(b, points[1], points[2], 0),
            pymunk.Segment(b, points[2], points[3], 0),
        )

    def add_rects(self, rects: List[RectObject]):
        rects = sorted(rects, key=lambda x: x.width * x.height, reverse=True)
        y_counter = 0
        for rect in rects:
            rects = rect
            x_pos = random.randint(0, int(self._box_rect.width - rect.width))
            y_pos = y_counter
            y_counter -= rects.height - 10

            inertia = pymunk.moment_for_box(self.config.body_mass, (rects.width, rects.height))
            body = pymunk.Body(self.config.body_mass, inertia)
            body.position = (x_pos + rects.width / 2, y_pos + rects.height / 2)

            shape = pymunk.Poly.create_box(body, (rects.width, rects.height))
            shape.friction = self.config.body_friction
            shape.elasticity = self.config.body_elasticity
            shape.source_object = rect

            self.space.add(body, shape)
            self. _rectangles.append((rects, body, shape))

        self._trackers = [BodyTracker(body) for body in self.space.bodies if body.body_type == pymunk.Body.DYNAMIC]

    def get_colliding_pairs(self):
        colliding = []
        shapes = self.space.shapes
        for i in range(len(shapes)):
            for j in range(i + 1, len(shapes)):
                s1, s2 = shapes[i], shapes[j]
                if s1.shapes_collide(s2).points:
                    colliding.append((s1, s2))
        return colliding

    def update(self, dt):
        self._update_trackers()

        if self._stationary_counter > 3:
            if not self._rotation_done:
                self._rotate_next_rectangle()
                if self._rotation_index >= len(self._rectangles):
                    self._shake_timer = 4
                    self._shake_strength = 2
            elif self._shake_timer < 0 and not self._empty_filled:
                self._fill_empty_areas()
                self._shake_timer = 4

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

        # Целевые углы: вертикальное положение (π/2 и 3π/2)
        vertical_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]

        # Найти ближайший вертикальный угол
        closest_angle = min(vertical_angles, key=lambda a: abs(a - current_angle))

        body.angle = closest_angle
        body.angular_velocity = 0
        body.moment = float("inf")
        self.space.reindex_shapes_for_body(body)
        self._rotation_index += 1

    def _calculate_overlap_area(self, shape_a, shape_b):
        # Реализовать расчет площади пересечения shape_a и shape_b
        # Вариант: использовать библиотеку shapely, если полигоны можно представить
        from shapely.geometry import Polygon

        def to_polygon(shape):
            return Polygon([shape.body.local_to_world(v) for v in shape.get_vertices()])

        poly_a = to_polygon(shape_a)
        poly_b = to_polygon(shape_b)

        if poly_a.intersects(poly_b):
            return poly_a.intersection(poly_b).area
        return 0

    def _fill_empty_areas(self):
        self._empty_areas = find_empty_areas(self.get_parent_image())

        rects_to_place = [
            (rect, body, shape)
            for rect, body, shape in self._rectangles
            if body.position.y + rect.height / 2 < self._box_rect.y
        ]

        for empty_area in self._empty_areas:
            ex, ey, ew, eh = empty_area
            for i, (rect, body, shape) in enumerate(rects_to_place):
                rw, rh = rect.width, rect.height
                can_fit_normal = rw <= ew and rh <= eh
                can_fit_rotated = rh <= ew and rw <= eh

                if can_fit_normal or can_fit_rotated:
                    if not can_fit_normal:
                        body.angle = math.pi / 2  # 90 градусов
                    else:
                        body.angle = 0

                    rw, rh = rect.width, rect.height
                    body.position = (ex + rw / 2, ey + rh / 2)
                    body.velocity = (0, 0)
                    self.space.reindex_shapes_for_body(body)
                    del rects_to_place[i]
                    break

        self._empty_filled = True

    def _shake(self, strength=10000):
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                dx = random.uniform(-strength, strength)
                dy = random.uniform(-strength, strength)
                body.apply_impulse_at_local_point((dx, dy))

    def get_drawable_objects(self):
        return self._rectangles

    def get_segments(self):
        return [s for s in self.space.shapes if isinstance(s, pymunk.Segment)]

    def get_parent_image(self):
        surface = self._render()
        surf_array = pygame.surfarray.array3d(surface)  # shape: (width, height, 3)
        image_np = np.transpose(surf_array, (1, 0, 2))  # shape: (height, width, 3)

        return image_np

    def _render(self):
        self._subsurface.fill(Colors.WHITE)

        for seg in self.get_segments():
            start = int(seg.a.x), int(seg.a.y)
            end = int(seg.b.x), int(seg.b.y)
            pygame.draw.line(self._subsurface, (23, 22, 110), start, end, 3)

        for rect, body, shape in self.get_drawable_objects():
            surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            surface.fill(shape.source_object.back_color)
            angle_degrees = -body.angle * 180 / math.pi
            rotated = pygame.transform.rotate(surface, angle_degrees)
            rotated_rect = rotated.get_rect(center=(int(body.position.x), int(body.position.y)))
            self._subsurface.blit(rotated, rotated_rect)

        pygame.draw.rect(self._subsurface, Colors.BLACK, (0, 0, self._box_rect.width, self._box_rect.height))

        return self._subsurface

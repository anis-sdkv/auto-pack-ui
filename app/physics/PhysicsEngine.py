import cv2
import numpy as np
import pymunk
import random
import math

import pygame

from app.common import Colors
from app.physics.BodyTracker import BodyTracker
from app.physics.EmptyAreaFinder import find_empty_areas


class PhysicsEngine:
    def __init__(self, box_rect: pygame.Rect, parent, speed_multiplier=1):
        self.parent = parent
        self.speed_multiplier = speed_multiplier
        self.space = pymunk.Space()
        self.space.gravity = (0, 1000)
        self.space.damping = 0.9
        self.space.iterations = 50
        self.space.collision_slop = 0.01

        self._create_boundaries(box_rect)

        self.rectangles = []
        self.shake_timer = 10
        self._setup_collision_handler()

        self.rotation_index = 0
        self.rotation_done = False

        self.empty_areas = []

    def _setup_collision_handler(self):
        self.collision_handler = self.space.add_default_collision_handler()
        self.collision_handler.begin = self._on_collision_begin

    def _on_collision_begin(self, arbiter, space, data):
        return True

    def _create_boundaries(self, rect: pygame.Rect):
        s = self.space
        b = s.static_body

        points = [
            (rect.x, -10000),
            (rect.x, rect.y + rect.h),
            (rect.x + rect.w, rect.y + rect.h),
            (rect.x + rect.w, -10000),
        ]

        s.add(
            pymunk.Segment(b, points[0], points[1], 0),
            pymunk.Segment(b, points[1], points[2], 0),
            pymunk.Segment(b, points[2], points[3], 0),
        )

    def add_rects(self, rect_obj):
        rect_obj = sorted(rect_obj, key=lambda x: x.rect.w * x.rect.h, reverse=True)
        y_counter = 0
        for obj in rect_obj:
            rect = obj.rect
            x = rect.x
            y = y_counter
            y_counter -= rect.h - 10

            mass = 0.1
            inertia = pymunk.moment_for_box(mass, (rect.width, rect.height))
            body = pymunk.Body(mass, inertia)
            body.position = (x + rect.width / 2, y + rect.height / 2)

            shape = pymunk.Poly.create_box(body, (rect.width, rect.height))
            shape.friction = 0
            shape.elasticity = 0
            shape.source_object = obj

            self.space.add(body, shape)
            self.rectangles.append((rect, body, shape))

        self.trackers = [BodyTracker(body) for body in self.space.bodies if body.body_type == pymunk.Body.DYNAMIC]

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

        all = 0
        for tracker in self.trackers:
            if not tracker.is_stationary():
                all += 1
            tracker.update()

        if all == 0 and not self.rotation_done:
            if self.rotation_index < len(self.rectangles):
                rect, body, shape = self.rectangles[self.rotation_index]

                # Повернуть на 90 градусов
                body.angle = math.pi / 2
                body.angular_velocity = 0

                # Запретить вращение
                body.moment = float("inf")
                self.space.reindex_shapes_for_body(body)

                self.rotation_index += 1
            else:
                self.rotation_done = True

        if self.rotation_done:
            self.empty_areas = find_empty_areas(self.get_parent_image())

        for _ in range(self.speed_multiplier):
            # if self.shake_timer > 0:
            #     if self.shake_timer < 2:
            #         self._shake(strength=10)
            #     else:
            #         self._shake(strength=5)
            #     self.shake_timer -= dt
            self.space.step(dt)

    def _shake(self, strength=10000):
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                dx = random.uniform(-strength, strength)
                dy = random.uniform(-strength, strength)
                body.apply_impulse_at_local_point((dx, dy))

    def get_drawable_objects(self):
        return self.rectangles

    def get_segments(self):
        return [s for s in self.space.shapes if isinstance(s, pymunk.Segment)]

    def get_parent_image(self):
        surface = self.parent._render()
        surf_array = pygame.surfarray.array3d(surface)  # shape: (width, height, 3)
        image_np = np.transpose(surf_array, (1, 0, 2))  # shape: (height, width, 3)

        return image_np

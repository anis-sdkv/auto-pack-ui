import math
import random
import pygame
import pymunk
import pymunk.pygame_util

from utils.PackingDataV2 import PackingDataV2


class ShakeStabilityCalculator:
    def __init__(self, data: PackingDataV2):
        self.box_width = data.box_width
        self.box_height = data.box_height
        self.objects = data.objects
        self.space = pymunk.Space()
        self.bodies = []

        # Настройка pygame
        pygame.init()
        self.screen = pygame.display.set_mode((int(self.box_width), int(self.box_height)))
        pygame.display.set_caption("Shake Stability Visualization")
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        self.setup_scene()

    def correct_positions(self):
        for obj in self.objects:
            self.correct_object_position(obj, self.box_width, self.box_height)

    def correct_object_position(self, obj, box_width, box_height, margin=1):
        # Сдвигаем влево, если вылазит за левую границу
        if obj['x'] < margin:
            obj['x'] = margin
        # Сдвигаем вправо, если вылазит за правую границу
        if obj['x'] + obj['w'] > box_width - margin:
            obj['x'] = box_width - obj['w'] - margin
        # Сдвигаем вверх, если вылазит за верхнюю границу
        if obj['y'] < margin:
            obj['y'] = margin
        # Сдвигаем вниз, если вылазит за нижнюю границу
        if obj['y'] + obj['h'] > box_height - margin:
            obj['y'] = box_height - obj['h'] - margin

    def setup_scene(self):
        self.correct_positions()

        # Создаем границы контейнера
        points = [
            (0, 0),
            (self.box_width, 0),
            (self.box_width, self.box_height),
            (0, self.box_height)
        ]

        static_lines = [
            pymunk.Segment(self.space.static_body, points[0], points[1], 1),
            pymunk.Segment(self.space.static_body, points[1], points[2], 1),
            pymunk.Segment(self.space.static_body, points[2], points[3], 1),
            pymunk.Segment(self.space.static_body, points[3], points[0], 1)
        ]
        for line in static_lines:
            line.friction = 0.5
            self.space.add(line)

        # Добавляем объекты как динамические тела
        for obj in self.objects:
            mass = 100
            width = obj['w']
            height = obj['h']
            moment = pymunk.moment_for_box(mass, (width, height))
            body = pymunk.Body(mass, moment)
            body.position = obj['x'] + width / 2, obj['y'] + height / 2
            shape = pymunk.Poly.create_box(body, (width, height))
            shape.friction = 0.5
            self.space.add(body, shape)
            self.bodies.append(body)

    def apply_random_shake(self, force_magnitude=5000):
        for body in self.bodies:
            fx = random.uniform(-force_magnitude, force_magnitude)
            fy = random.uniform(-force_magnitude, force_magnitude)
            body.apply_impulse_at_local_point((fx, fy))

    def simulate(self, steps=100, dt=1 / 60):
        for i in range(steps):
            if i % 10 == 0:
                self.apply_random_shake()
            self.space.step(dt)

    def simulate_and_visualize(self, steps=300, dt=1 / 60):
        clock = pygame.time.Clock()
        for step in range(steps):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            if step % 10 == 0:
                self.apply_random_shake(20000)
            self.space.step(dt)

            self.screen.fill((255, 255, 255))  # Белый фон
            self.space.debug_draw(self.draw_options)
            pygame.display.flip()
            clock.tick(60)

    def calculate_average_displacement(self):
        initial_positions = [body.position for body in self.bodies]

        self.simulate()

        # Считаем смещения
        total_displacement = 0
        for i, body in enumerate(self.bodies):
            dx = body.position[0] - initial_positions[i][0]
            dy = body.position[1] - initial_positions[i][1]
            displacement = math.sqrt(dx ** 2 + dy ** 2)
            total_displacement += displacement

        average_displacement = total_displacement / len(self.bodies) if self.bodies else 0
        diagonal = math.hypot(self.box_width, self.box_height)
        normalized_displacement = average_displacement / diagonal if diagonal > 0 else 0
        return normalized_displacement

    def run(self):
        self.simulate_and_visualize()
        avg_disp = self.calculate_average_displacement()
        print(f"Среднее смещение после тряски: {avg_disp:.2f} пикселей")
        pygame.quit()
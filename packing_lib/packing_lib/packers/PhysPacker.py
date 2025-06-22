import time
import math
from typing import List, Optional

import pygame

from packing_lib.packing_lib._phys_engine.PhysicsEngine import PhysicsEngine
from packing_lib.packing_lib._phys_engine.Renderer import PygameRenderer, HeadlessRenderer
from packing_lib.packing_lib.interfaces.BasePacker import BasePacker
from packing_lib.packing_lib.types import PackingInputTask, PlacedObject, PackingContainer, PackInput


class PhysPacker(BasePacker):
    def __init__(self, headless=False, pixels_per_mm=10, simulation_speed=1.0, target_fps=60):
        """
        Args:
            headless: режим без визуализации (максимальная скорость)
            pixels_per_mm: масштаб для визуализации
            simulation_speed: множитель скорости симуляции (только для визуализации)
            target_fps: целевой FPS для визуализации
        """
        self.headless = headless
        if pixels_per_mm <= 0:
            raise ValueError("pixels_per_mm должен быть больше 0")
        self.pixels_per_mm = pixels_per_mm
        self.simulation_speed = max(0.1, simulation_speed)  # минимум 0.1x
        self.target_fps = max(1, target_fps)  # минимум 1 FPS

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
        
        # Проверяем близость к 90° (π/2) с допуском
        tolerance = math.pi / 4  # 45 градусов
        
        if math.pi / 2 - tolerance < angle < math.pi / 2 + tolerance:
            # 90° - поворот на 90 градусов
            return original_height, original_width
        else:
            # 0° или любой другой угол - исходные размеры
            return original_width, original_height

    def pack(self, task: PackingInputTask) -> List[PlacedObject]:
        # Масштабирование из мм в пиксели
        scaled_container = PackingContainer(
            width=task.container.width * self.pixels_per_mm,
            height=task.container.height * self.pixels_per_mm,
            padding=task.container.padding * self.pixels_per_mm
        )
        
        scaled_objects = [
            PackInput(
                id=obj.id,
                width=obj.width * self.pixels_per_mm,
                height=obj.height * self.pixels_per_mm
            ) for obj in task.objects
        ]
        
        bin_w, bin_h = int(scaled_container.width), int(scaled_container.height)
        
        screen = None
        clock = None
        
        if not self.headless:
            pygame.init()
            screen = pygame.display.set_mode((bin_w, bin_h))
            pygame.display.set_caption("Physics Packing Visualization")
            clock = pygame.time.Clock()
            renderer = PygameRenderer()
        else:
            renderer = HeadlessRenderer()

        engine = PhysicsEngine(scaled_container, renderer=renderer)
        engine.add_rects(scaled_objects)

        dt = 1 / 60  # базовый timestep для физики

        if self.headless:
            # Headless режим - максимальная скорость
            while not engine.done:
                engine.update(dt)
        else:
            # Режим с визуализацией
            while not engine.done:
                # Обработка событий
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return []

                # Выполняем несколько шагов симуляции за кадр в зависимости от скорости
                steps_per_frame = max(1, int(self.simulation_speed))
                for _ in range(steps_per_frame):
                    if not engine.done:
                        engine.update(dt)

                # Отрисовка только финального состояния за кадр
                surface = engine._render()
                if surface:
                    screen.blit(surface, (0, 0))
                    pygame.display.flip()
                    clock.tick(self.target_fps)


        if not self.headless:
            pygame.quit()

        placed = []
        for rect, body, shape in engine.get_drawable_objects():
            # Вычисляем актуальные размеры с учетом поворота
            original_width = rect.width / self.pixels_per_mm
            original_height = rect.height / self.pixels_per_mm
            actual_width, actual_height = self._get_actual_dimensions(
                original_width, original_height, body.angle
            )
            
            # Проверяем, что объект находится внутри контейнера
            container_width = task.container.width
            container_height = task.container.height
            center_x = body.position.x / self.pixels_per_mm
            center_y = body.position.y / self.pixels_per_mm
            
            # Объект считается внутри контейнера, если его границы не выходят за пределы
            if (center_x - actual_width / 2 >= 0 and
                center_x + actual_width / 2 <= container_width and
                center_y - actual_height / 2 >= 0 and
                center_y + actual_height / 2 <= container_height):
                
                placed.append(PlacedObject(
                    id=shape.source_object.id,
                    center_x=center_x,
                    center_y=center_y,
                    width=actual_width,
                    height=actual_height,
                ))

        return placed

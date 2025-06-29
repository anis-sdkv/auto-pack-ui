import time
import math
from typing import List, Optional

import pygame

from packing_lib.packing_lib._phys_engine.PhysicsEngine import PhysicsEngine
from packing_lib.packing_lib._phys_engine.Renderer import PygameRenderer
from packing_lib.packing_lib.interfaces.BasePacker import BasePacker
from packing_lib.packing_lib.types import PackingInputTask, PlacedObject, PackingContainer, PackInputObject, SortOrder


class PhysPacker(BasePacker):
    def __init__(self, headless=False, render_scale=1, simulation_speed=1.0, target_fps=60, sort_order=SortOrder.DESCENDING):
        self.headless = headless
        if render_scale <= 0:
            raise ValueError("pixels_per_mm должен быть больше 0")
        self.pixels_per_mm = render_scale
        self.simulation_speed = max(0.1, simulation_speed)
        self.target_fps = max(1, target_fps)
        self.sort_order = sort_order


    def pack(self, task: PackingInputTask) -> List[PlacedObject]:
        container = task.container
        objects = task.objects

        bin_w = int(container.width * self.pixels_per_mm)
        bin_h = int(container.height * self.pixels_per_mm)
        
        screen = None
        clock = None
        renderer = None
        
        if not self.headless:
            pygame.init()
            screen = pygame.display.set_mode((bin_w, bin_h))
            pygame.display.set_caption("Physics Packing Visualization")
            clock = pygame.time.Clock()
            renderer = PygameRenderer(self.pixels_per_mm)
            renderer.initialize(container)

        engine = PhysicsEngine(container, sort_order=self.sort_order)
        engine.add_rects(objects)

        dt = 1 / 60

        if self.headless:
            while not engine.done:
                engine.update(dt)
        else:
            while not engine.done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return []

                steps_per_frame = max(1, int(self.simulation_speed))
                for _ in range(steps_per_frame):
                    if not engine.done:
                        engine.update(dt)

                if renderer:
                    surface = renderer.render(engine.get_drawable_objects(), engine.get_segments())
                    if surface:
                        screen.blit(surface, (0, 0))
                        pygame.display.flip()
                        clock.tick(self.target_fps)


        if not self.headless:
            pygame.quit()

        placed = []
        for rect, body, shape in engine.get_drawable_objects():
            actual_width, actual_height = engine._get_actual_dimensions(
                rect.width, rect.height, body.angle
            )
            
            placed.append(PlacedObject(
                id=shape.source_object.id,
                center_x=body.position.x,
                center_y=body.position.y,
                width=actual_width,
                height=actual_height,
            ))

        return placed

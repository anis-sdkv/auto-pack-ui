import time
from typing import List

import pygame

from packing_lib.packing_lib._phys_engine.PhysicsEngine import PhysicsEngine
from packing_lib.packing_lib.interfaces.BasePacker import BasePacker
from packing_lib.packing_lib.types import PackingTask, PlacedObject


class PhysPacker(BasePacker):
    def __init__(self, timeout_seconds=5):
        self.timeout_seconds = timeout_seconds

    # def pack(self, task: PackingTask) -> List[PlacedObject]:
    #     bin_w, bin_h = task.container.width, task.container.height
    #
    #     box_rect = pygame.Rect(0, 0, bin_w, bin_h)
    #     engine = PhysicsEngine(box_rect)
    #
    #     engine.add_rects(task.objects)
    #
    #     start_time = time.time()
    #     dt = 1 / 60
    #
    #     while not engine.done and (time.time() - start_time < self.timeout_seconds):
    #         engine.update(dt)
    #         time.sleep(dt)
    #
    #     placed = []
    #     for rect, body, shape in engine.get_drawable_objects():
    #         placed.append(PlacedObject(
    #             id=shape.source_object.id,
    #             x=body.position.x - rect.width / 2,
    #             y=body.position.y - rect.height / 2,
    #             width=rect.width,
    #             height=rect.height,
    #         ))
    #
    #     return placed

    def pack(self, task: PackingTask) -> List[PlacedObject]:
        bin_w, bin_h = task.container.width, task.container.height

        pygame.init()
        screen = pygame.display.set_mode((bin_w, bin_h))
        pygame.display.set_caption("Physics Packing Visualization")

        box_rect = pygame.Rect(0, 0, bin_w, bin_h)
        engine = PhysicsEngine(box_rect)

        engine.add_rects(task.objects)

        clock = pygame.time.Clock()
        start_time = time.time()
        dt = 1 / 60

        while not engine.done and (time.time() - start_time < self.timeout_seconds):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return []

            engine.update(dt)

            # Визуализация
            screen.blit(engine._render(), (0, 0))
            pygame.display.flip()

            clock.tick(60)  # Ограничение FPS до 60

        pygame.quit()

        placed = []
        for rect, body, shape in engine.get_drawable_objects():
            placed.append(PlacedObject(
                id=shape.source_object.id,
                x=body.position.x - rect.width / 2,
                y=body.position.y - rect.height / 2,
                width=rect.width,
                height=rect.height,
            ))

        return placed

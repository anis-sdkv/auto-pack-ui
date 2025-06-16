import copy
import math
import random
import pygame

from app.custom_elements.DrawableRect import DrawableRect
from app.packers.NFDHPacker import NFDHPacker
from packing_lib.packing_lib._phys_engine.PhysicsEngine import PhysicsEngine
from utils.PackingData import PackingData


class Benchmark:
    def __init__(self, base_path):
        self.base_path = base_path
        self.width = 400
        self.height = 400
        self.boxes_to_pack = []

        self.greedy_packer = NFDHPacker(self.width, self.height)
        self.phys_engine = PhysicsEngine(pygame.Rect(0, 0, self.width, self.height),
                                         pygame.Surface((self.width, self.height)))
        self.packing_data = PackingData(self.width, self.height)

        self.path_for_greedy = None

    def start_bench(self, dataset_name):
        self.create_random_items(40)
        samples = 10

        for i in range(samples):
            self.path_for_greedy = f"{self.base_path}/dataset_{dataset_name}/greedy/launch_{i}.json"
            self.process_greedy()

        for i in range(samples):
            path = f"{self.base_path}/dataset_{dataset_name}/phys/launch_{i}.json"
            self.process_phys(path)

    def create_random_items(self, count: int):
        for i in range(count):
            width, height = random.randint(30, 100), random.randint(30, 100)
            x_pos = random.randint(0, self.width - width)
            y_pos = random.randint(0, self.height - height)

            self.boxes_to_pack.append(DrawableRect(pygame.Rect(x_pos, y_pos, width, height)))

    def process_phys(self, path):
        self.phys_engine = PhysicsEngine(pygame.Rect(0, 0, self.width, self.height),
                                         pygame.Surface((self.width, self.height)))
        print("phys started")
        self.phys_engine.add_rects(self.boxes_to_pack)

        clock = pygame.time.Clock()
        fps = 60

        while not self.phys_engine.done:
            time_delta = clock.tick(fps) / 1000.0
            self.phys_engine.update(1)

        print("phys end")
        packed = self.extract()
        packed = [i for i in packed if i.rect.y >= 0]
        self.save(packed, path)

    def extract(self):
        placed_rects = []
        for rect, body, shape in self.phys_engine.get_drawable_objects():
            surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            angle_degrees = -body.angle * 180 / math.pi
            rotated = pygame.transform.rotate(surface, angle_degrees)
            rotated_rect = rotated.get_rect(center=(int(body.position.x), int(body.position.y)))

            new_rect = copy.deepcopy(shape.source_object)
            new_rect.rect = rotated_rect
            placed_rects.append(new_rect)
        return placed_rects

    def process_greedy(self):
        self.greedy_packer.start(self.boxes_to_pack, self._on_packing_completed)

    def save(self, packed, path):
        self.packing_data.clear()
        self.packing_data.add_objects(packed)
        self.packing_data.save_to_file(path)

    def _on_packing_completed(self, packed):
        self.save(packed, self.path_for_greedy)


if __name__ == "__main__":
    bench = Benchmark("../out/bench")
    bench.start_bench("test2")

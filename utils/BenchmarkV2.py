import random
import os
from typing import List

from packing_lib.packing_lib.interfaces.BasePacker import BasePacker
from packing_lib.packing_lib.packers.BranchAndBoundPacker import BranchAndBoundPacker
from packing_lib.packing_lib.packers.ExactORToolsPacker import ExactORToolsPacker
from packing_lib.packing_lib.packers.NFDHPacker import NFDHPacker
from packing_lib.packing_lib.types import PackingTask, Container, RectObject, PlacedObject
from utils.PackingDataV2 import PackingDataV2


class BenchmarkV2:
    def __init__(self, base_path: str, packers: List[BasePacker]):
        self.base_path = base_path
        self.packers = packers
        self.container_width = 200
        self.container_height = 200
        self.container = Container((0, 0), self.container_width, self.container_height)

    def start_bench(self, dataset_name: str, num_samples: int = 10, num_objects: int = 40):
        for packer in self.packers:
            packer_name = self._get_packer_name(packer)
            print(f"Benchmarking {packer_name}...")

            for i in range(num_samples):
                objects = self.create_random_items(num_objects)
                task = PackingTask(container=self.container, objects=objects)
                packed = packer.pack(task)

                dir_path = os.path.join(self.base_path, f"dataset_{dataset_name}", packer_name)
                os.makedirs(dir_path, exist_ok=True)
                file_path = os.path.join(dir_path, f"launch_{i}.json")

                self.save(packed, file_path)

    def _get_packer_name(self, packer) -> str:
        return packer.__class__.__name__.replace("Packer", "").lower()

    def create_random_items(self, count: int) -> List[RectObject]:
        objects = []
        for i in range(count):
            w = random.randint(30, 100)
            h = random.randint(30, 100)
            cx = random.uniform(w / 2, self.container_width - w / 2)
            cy = random.uniform(h / 2, self.container_height - h / 2)

            obj = RectObject(
                id=i,
                center_mm=(cx, cy),
                angle_deg=0.0,
                width=w,
                height=h,
                z=0.0,
            )
            objects.append(obj)
        return objects

    def save(self, packed: List[PlacedObject], path: str):
        packing_data = PackingDataV2(self.container_width, self.container_height)
        packing_data.clear()
        packing_data.add_objects(packed)
        packing_data.save_to_file(path)


if __name__ == "__main__":
    bench = BenchmarkV2(
        base_path="../out/bench",
        packers=[
            NFDHPacker(),
            ExactORToolsPacker()
        ]
    )
    bench.start_bench(dataset_name="test_multi", num_samples=10, num_objects=9)

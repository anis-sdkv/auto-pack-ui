from abc import ABC, abstractmethod
from typing import List

from packing_lib.packing_lib.types import PackingTask, PlacedObject


class BasePacker(ABC):
    @abstractmethod
    def pack(self, task: PackingTask) -> List[PlacedObject]:
        pass
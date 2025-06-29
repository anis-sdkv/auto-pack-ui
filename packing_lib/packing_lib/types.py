from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum

import numpy as np


class SortOrder(Enum):
    DESCENDING = "descending"
    ASCENDING = "ascending"
    RANDOM = "random"


@dataclass
class RectObject:
    id: int
    center_mm: (float, float)
    angle_deg: float
    width: float
    height: float
    z: float


@dataclass
class PackingContainer:
    width: float
    height: float
    padding: float = 0.0


@dataclass
class PlacedObject:
    id: int
    center_x: float
    center_y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.center_x - self.width / 2

    @property
    def top(self) -> float:
        return self.center_y - self.height / 2


@dataclass
class ArucoResult:
    id: int
    bounding_box: np.ndarray
    rvec: np.ndarray
    tvec: np.ndarray


@dataclass
class RawObject:
    id: int
    bounding_box: Tuple[Tuple[float, float], Tuple[float, float], float]  # ((cx, cy), (w, h), angle)


@dataclass
class SceneProcessResult:
    markers: List[ArucoResult]
    raw_objects: List[RawObject]
    converted_objects: List[RectObject]
    reference_marker: Optional['ArucoResult'] = None
    scale: Optional[float] = None


@dataclass
class PackInputObject:
    id: int
    width: float
    height: float


@dataclass
class PackingInputTask:
    container: PackingContainer
    objects: List[PackInputObject]

    @staticmethod
    def from_rect_objects(rect_objects: List[RectObject]) -> List[PackInputObject]:
        return [
            PackInputObject(id=obj.id, width=obj.width, height=obj.height)
            for obj in rect_objects
        ]


@dataclass
class InputInstruction:
    x: float
    y: float
    z: float
    theta: float
    w: float
    h: float


@dataclass
class OutputInstruction:
    x: float
    y: float
    z: float
    theta: float
    w: float
    h: float


@dataclass
class ManipulatorInstruction:
    id: int
    input: InputInstruction
    output: OutputInstruction

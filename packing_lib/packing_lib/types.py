from dataclasses import dataclass
from typing import Tuple, List

import numpy as np


@dataclass
class RectObject:
    id: int
    center_mm: (float, float)
    angle_deg: float
    width: float
    height: float
    z: float


@dataclass
class Container:
    left_top_point: (float, float)
    width: float
    height: float
    padding: float = 0.0


@dataclass
class PackingTask:
    container: Container
    objects: List[RectObject]

@dataclass
class PlacedObject:
    id: int
    x: float
    y: float
    width: float
    height: float


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

# @dataclass
# class PackInput:
#     id: int
#     width: float
#     height: float

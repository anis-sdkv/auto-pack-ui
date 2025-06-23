from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum

import numpy as np


class SortOrder(Enum):
    """Порядок сортировки объектов при сбросе в физическую симуляцию"""
    DESCENDING = "descending"  # по убыванию (крупные вниз) - дефолт
    ASCENDING = "ascending"    # по возрастанию (мелкие вниз)
    RANDOM = "random"          # случайный порядок


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
    center_x: float  # центр объекта
    center_y: float  # центр объекта
    width: float
    height: float
    
    @property
    def left(self) -> float:
        """Координата левой границы объекта"""
        return self.center_x - self.width / 2
    
    @property
    def top(self) -> float:
        """Координата верхней границы объекта"""
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
    """Параметры захвата объекта"""
    x: float      # координаты центра в сцене
    y: float      
    z: float      # расстояние до объекта
    theta: float  # угол ориентации (градусы)
    w: float      # исходные размеры
    h: float


@dataclass  
class OutputInstruction:
    """Параметры размещения объекта в контейнере"""
    x: float      # координаты в контейнере
    y: float
    z: float      # высота сброса (пока заглушка)
    theta: float  # угол поворота (0°, 90°, 180°, 270°)
    w: float      # размеры после поворота
    h: float


@dataclass
class ManipulatorInstruction:
    """Полная инструкция для манипулятора: захват + размещение"""
    id: int
    input: InputInstruction
    output: OutputInstruction

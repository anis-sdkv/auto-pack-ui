from dataclasses import dataclass
from typing import Tuple, List, Optional

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
    
    @property
    def right(self) -> float:
        """Координата правой границы объекта"""
        return self.center_x + self.width / 2
    
    @property
    def bottom(self) -> float:
        """Координата нижней границы объекта"""
        return self.center_y + self.height / 2
    
    # Для обратной совместимости (deprecated)
    @property
    def x(self) -> float:
        """Deprecated: используйте left"""
        return self.left
    
    @property
    def y(self) -> float:
        """Deprecated: используйте top"""
        return self.top


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
class PackInput:
    id: int
    width: float
    height: float


@dataclass
class PackingInputTask:
    container: PackingContainer
    objects: List[PackInput]

    @staticmethod
    def from_rect_objects(rect_objects: List[RectObject]) -> List[PackInput]:
        return [
            PackInput(id=obj.id, width=obj.width, height=obj.height)
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

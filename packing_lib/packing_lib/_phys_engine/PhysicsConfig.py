import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class PhysicsConfig:
    space_gravity: Tuple[float, float] = (0, 1000)
    space_damping: float = 0.9
    space_iterations: int = 50
    space_collision_slop: float = 0.01

    body_mass: float = 0.1
    body_friction: float = 0.5
    body_elasticity: float = 0

    stationary_frames: int = 3
    shake_strength: float = 10
    rotation_angles_deg: Tuple[int, ...] = (0, 90)
    simulation_speed_multiplier = 1
    
    # Временные параметры
    shake_duration: float = 4.0
    stationary_threshold: int = 3
    initial_shake_strength: float = 10.0
    post_rotation_shake_strength: float = 2.0
    
    # Размещение объектов
    object_spacing: float = 10.0
    boundary_depth: float = 10000.0
    
    # Детекция движения
    position_threshold: float = 3.0
    angle_threshold: float = 0.03
    
    # Встряхивание
    default_shake_force: float = 10000.0

    @property
    def rotation_angles_rad(self):
        return tuple(math.radians(a) for a in self.rotation_angles_deg)
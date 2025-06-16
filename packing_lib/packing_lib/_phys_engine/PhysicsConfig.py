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
    rotation_angles_deg: Tuple[int, ...] = (0, 90, 180, 270)
    simulation_speed_multiplier = 1

    @property
    def rotation_angles_rad(self):
        return tuple(math.radians(a) for a in self.rotation_angles_deg)
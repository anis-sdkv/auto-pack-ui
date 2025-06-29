import pygame
import threading
from typing import Optional

from app.screens.base.ScreenBase import ScreenBase
from app.common import Colors
from app.MainScreenState import main_screen_state
from packing_lib.packing_lib.packers.PhysPacker import PhysPacker
from packing_lib.packing_lib._phys_engine.PhysicsEngine import PhysicsEngine
from packing_lib.packing_lib._phys_engine.Renderer import PygameRenderer
from packing_lib.packing_lib.types import PackingInputTask, PlacedObject


class PhysVisualizationScreen(ScreenBase):
    def __init__(self, context, task_data: PackingInputTask):
        super().__init__(context)
        self.task_data = task_data
        self.physics_engine: Optional[PhysicsEngine] = None
        self.renderer: Optional[PygameRenderer] = None
        self.pixels_per_mm = 2
        self.simulation_speed = 2.0
        self.target_fps = 60
        self.clock = pygame.time.Clock()
        
        self.simulation_running = False
        self.simulation_done = False
        self.result = []
        
        self._start_simulation()
    
    def _start_simulation(self):
        container = self.task_data.container
        objects = self.task_data.objects
        
        self.physics_engine = PhysicsEngine(container)
        self.physics_engine.add_rects(objects)
        
        self.renderer = PygameRenderer(self.pixels_per_mm)
        self.renderer.initialize(container)
        
        self.simulation_running = True
        
    def update(self, time_delta: float):
        if self.simulation_running and self.physics_engine:
            dt = 1 / 60
            steps_per_frame = max(1, int(self.simulation_speed))
            
            for _ in range(steps_per_frame):
                if not self.physics_engine.done:
                    self.physics_engine.update(dt)
                else:
                    self.simulation_running = False
                    self.simulation_done = True
                    self._extract_result()
                    self._return_to_main_screen()
                    break
    
    def _extract_result(self):
        if self.physics_engine:
            for rect, body, shape in self.physics_engine.get_drawable_objects():
                actual_width, actual_height = self.physics_engine._get_actual_dimensions(
                    rect.width, rect.height, body.angle
                )
                
                self.result.append(PlacedObject(
                    id=shape.source_object.id,
                    center_x=body.position.x,
                    center_y=body.position.y,
                    width=actual_width,
                    height=actual_height,
                ))
    
    def draw(self):
        self.surface.fill(Colors.WHITE)
        
        if self.renderer and self.physics_engine:
            physics_surface = self.renderer.render(
                self.physics_engine.get_drawable_objects(),
                self.physics_engine.get_segments()
            )
            
            if physics_surface:
                screen_rect = self.surface.get_rect()
                physics_rect = physics_surface.get_rect()
                
                x = (screen_rect.width - physics_rect.width) // 2
                y = (screen_rect.height - physics_rect.height) // 2
                
                self.surface.blit(physics_surface, (x, y))
    
    def handle_event(self, event):
        pass
    
    def _return_to_main_screen(self):
        from app.screens.MainScreen import MainScreen
        
        if self.simulation_done and self.result:
            main_screen_state.save_physics_result(self.result)
        
        self.screen_manager.switch_to(MainScreen)
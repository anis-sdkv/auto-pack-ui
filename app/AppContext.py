from pygame import Surface
from pygame_gui import UIManager
from app.AppConfig import AppConfig
from app.screens.base.ScreenManager import ScreenManager
from app.CameraController import CameraController


class AppContext:
    def __init__(self, screen, ui_manager, screen_manager):
        self.surface: Surface = screen
        self.ui_manager: UIManager = ui_manager
        self.screen_manager: ScreenManager = screen_manager
        self.config = AppConfig()
        self.camera_controller: CameraController = CameraController(self.config.stream_url)

from datetime import datetime

import pygame
import sys
import pygame_gui
from pygame import display

from app.AppContext import AppContext
from app.screens.ConfigScreen import ConfigScreen
from app.screens.MainScreen import MainScreen
from app.screens.base.ScreenManager import ScreenManager


class App(AppContext):
    DEFAULT_SCREEN_WIDTH: int = 800
    DEFAULT_SCREEN_HEIGHT: int = 800

    def __init__(self):
        pygame.init()

        self.running = True
        self.clock = pygame.time.Clock()
        self.fps = 60

        display.set_caption("Алгоритм упаковки")
        windows_size = (App.DEFAULT_SCREEN_WIDTH, App.DEFAULT_SCREEN_HEIGHT)

        screen = display.set_mode(windows_size, pygame.RESIZABLE)
        ui_manager = pygame_gui.UIManager(windows_size, "assets/themes/theme.json")
        screen_manager = ScreenManager(self)
        super().__init__(screen, ui_manager, screen_manager)

        self.screen_manager.switch_to(MainScreen)

    def run(self):
        while self.running:
            time_delta = self.clock.tick(self.fps) / 1000.0

            self.screen_manager.update(time_delta)
            self.ui_manager.update(time_delta)

            self.handle_events()

            self.screen_manager.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            self.ui_manager.process_events(event)
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.VIDEORESIZE:
                new_size = (event.w, event.h)
                self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
                self.ui_manager.set_window_resolution(new_size)
                self.screen_manager.current_screen.handle_resize(new_size)

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                self.screen_manager.handle_event(event)


app_instance = App()

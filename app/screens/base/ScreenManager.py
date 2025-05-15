import pygame
from pygame_gui import UIManager

from app.screens.base import ScreenBase


class ScreenManager:
    def __init__(self, context):
        self.current_screen: ScreenBase = None
        self.context = context

    def switch_to(self, screen: type[ScreenBase], *args):
        self.context.ui_manager.clear_and_reset()
        self.current_screen = screen(self.context, *args)

    def handle_event(self, event):
        if self.current_screen:
            self.current_screen.handle_event(event)

    def update(self, dt):
        if self.current_screen:
            self.current_screen.update(dt)

    def draw(self):
        if self.current_screen:
            self.current_screen.draw()
        pygame.display.flip()

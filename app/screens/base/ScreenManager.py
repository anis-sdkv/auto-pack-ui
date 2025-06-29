import pygame
from pygame_gui import UIManager

from app.screens.base import ScreenBase


class ScreenManager:
    def __init__(self, context):
        self.current_screen: ScreenBase = None
        self.context = context
        self.screens = {}  # Кеш экранов

    def switch_to(self, screen: type[ScreenBase], *args):
        self.context.ui_manager.clear_and_reset()
        
        # Сначала сохраняем текущий экран в кеше (если это MainScreen без параметров)
        if self.current_screen and not args:
            from app.screens.MainScreen import MainScreen
            if isinstance(self.current_screen, MainScreen):
                self.screens[MainScreen] = self.current_screen
        
        # Проверяем есть ли экран в кеше
        is_returning_to_cached = False
        if not args and screen in self.screens:
            self.current_screen = self.screens[screen]
            is_returning_to_cached = True
        else:
            self.current_screen = screen(self.context, *args)
            # Сохраняем экран в кеше только для экранов без параметров
            if not args:
                self.screens[screen] = self.current_screen
        
        # Вызываем on_show только при возврате к кешированному экрану
        if is_returning_to_cached and hasattr(self.current_screen, 'on_show'):
            self.current_screen.on_show()
    
    def get_screen(self, screen_type: type[ScreenBase]):
        """Возвращает экземпляр экрана из кеша"""
        return self.screens.get(screen_type)

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

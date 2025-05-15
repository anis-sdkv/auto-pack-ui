import pygame
from pygame import Event
from pygame_gui import elements, UIManager


class ButtonsPanel:
    def __init__(self, rect: pygame.Rect, ui_manager: UIManager):
        self.rect = rect
        self.buttons_size = (rect.w, 40)
        self.ui_manager = ui_manager
        self._init_ui_elements(ui_manager)

    def _init_ui_elements(self, ui_manager: UIManager):
        self.gen_button = elements.UIButton(
            relative_rect=self.create_button_rect(),
            text='Сгенерировать',
            manager=ui_manager)
        self.place_button = elements.UIButton(
            relative_rect=self.create_button_rect(),
            text='Разместить NFDH',
            manager=ui_manager)
        self.place_phys_button = elements.UIButton(
            relative_rect=self.create_button_rect(),
            text='Разместить физ.',
            manager=ui_manager)
        self.camera_button = elements.UIButton(
            relative_rect=self.create_button_rect(),
            text='',
            manager=ui_manager)
        self.process_button = elements.UIButton(
            relative_rect=self.create_button_rect(),
            text='',
            manager=ui_manager)
        self.fix_cam_button = elements.UIButton(
            relative_rect=self.create_button_rect(),
            text='',
            manager=ui_manager)

    def create_button_rect(self):
        return pygame.Rect((0, 0), self.buttons_size)

    def update_layout(self):
        button_panel_x = self.rect.x
        button_panel_y = self.rect.height // 2 - 80

        offset = 60

        self.gen_button.set_relative_position((button_panel_x, button_panel_y))
        self.place_button.set_relative_position((button_panel_x, button_panel_y + offset))
        self.place_phys_button.set_relative_position((button_panel_x, button_panel_y + offset * 2))
        self.camera_button.set_relative_position((button_panel_x, button_panel_y + offset * 3))
        self.process_button.set_relative_position((button_panel_x, button_panel_y + offset * 4))
        self.fix_cam_button.set_relative_position((button_panel_x, button_panel_y + offset * 5))

    def draw(self, surface: pygame.surface):
        self.ui_manager.draw_ui(surface)

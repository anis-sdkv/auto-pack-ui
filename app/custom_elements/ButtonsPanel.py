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
        self.place_exact_button = elements.UIButton(
            relative_rect=self.create_button_rect(),
            text='Точное размещение',
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
        self.cancel_button = elements.UIButton(
            relative_rect=self.create_button_rect(),
            text='Отменить',
            manager=ui_manager)
        self.settings_button = elements.UIButton(
            relative_rect=self.create_button_rect(),
            text='Настройки',
            manager=ui_manager)

    def create_button_rect(self):
        return pygame.Rect((0, 0), self.buttons_size)

    def update_layout(self):
        button_panel_x = self.rect.x
        
        offset = 50
        num_buttons = 9
        total_height = num_buttons * offset
        button_panel_y = (self.rect.height - total_height) // 2

        self.gen_button.set_relative_position((button_panel_x, button_panel_y))
        self.place_button.set_relative_position((button_panel_x, button_panel_y + offset))
        self.place_phys_button.set_relative_position((button_panel_x, button_panel_y + offset * 2))
        self.place_exact_button.set_relative_position((button_panel_x, button_panel_y + offset * 3))
        self.cancel_button.set_relative_position((button_panel_x, button_panel_y + offset * 4))
        self.camera_button.set_relative_position((button_panel_x, button_panel_y + offset * 5))
        self.process_button.set_relative_position((button_panel_x, button_panel_y + offset * 6))
        self.fix_cam_button.set_relative_position((button_panel_x, button_panel_y + offset * 7))
        self.settings_button.set_relative_position((button_panel_x, button_panel_y + offset * 8))

    def draw(self, surface: pygame.surface):
        self.ui_manager.draw_ui(surface)

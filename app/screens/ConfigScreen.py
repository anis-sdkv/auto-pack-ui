import pygame
import pygame_gui
from pygame_gui.elements import UITextEntryLine, UILabel, UIButton, UIPanel, UITextBox
from pygame import Rect, Event

from app.AppContext import AppContext
from app.common import Colors
from app.screens.base.ScreenBase import ScreenBase


class ConfigScreen(ScreenBase):
    def __init__(self, context: AppContext):
        super().__init__(context)

        self.panel_size = (400, 400)
        self._create_ui(self.surface.get_size())

    def _create_ui(self, screen_size):
        panel_x = (screen_size[0] - self.panel_size[0]) // 2
        panel_y = (screen_size[1] - self.panel_size[1]) // 2

        # Создаём панель-контейнер по центру
        self.panel = UIPanel(
            relative_rect=Rect((panel_x, panel_y), self.panel_size),
            manager=self.ui_manager
        )

        input_width = 300
        input_height = 35
        start_y = 20
        spacing = 70

        def label(text, offset_y, object_id=""):
            return UILabel(
                relative_rect=Rect((50, offset_y), (input_width, 25)),
                text=text,
                manager=self.ui_manager,
                container=self.panel,
                object_id=object_id
            )

        def input_field(offset_y, init_text):
            return UITextEntryLine(
                relative_rect=Rect((50, offset_y), (input_width, input_height)),
                initial_text=init_text,
                manager=self.ui_manager,
                container=self.panel
            )

        label("Ссылка на IP-камеру", start_y)
        self.stream_input = input_field(start_y + 25, self.config.stream_url)

        label("Ширина ящика (мм)", start_y + spacing)
        self.box_width_input = input_field(start_y + spacing + 25, str(self.config.box_width))

        label("Высота ящика (мм)", start_y + spacing * 2)
        self.box_height_input = input_field(start_y + spacing * 2 + 25, str(self.config.box_height))

        self.message_label = UITextBox(
            html_text="",
            relative_rect=Rect((50, start_y + spacing * 3), (input_width, 70)),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#error_message"
        )

        self.ok_button = UIButton(
            relative_rect=Rect((150, start_y + spacing * 3 + 70), (100, 40)),
            text="OK",
            manager=self.ui_manager,
            container=self.panel
        )

    def handle_event(self, event: Event):
        if event.ui_element == self.ok_button:
            self._apply_settings()

    def _apply_settings(self):

        try:
            width = float(self.box_width_input.get_text())
            height = float(self.box_height_input.get_text())

            self.config.stream_url = self.stream_input.get_text()
            self.config.box_width = width
            self.config.box_height = height
            print("Настройки применены:", self.config)

            # Локальный импорт для избежания циклической зависимости
            from app.screens.MainScreen import MainScreen
            self.screen_manager.switch_to(MainScreen)


        except ValueError:
            self.message_label.set_text("Ошибка: ширина и высота должны быть числами")

    def handle_resize(self, new_size):
        # Центрируем панель заново
        panel_x = (new_size[0] - self.panel_size[0]) // 2
        panel_y = (new_size[1] - self.panel_size[1]) // 2
        self.panel.set_relative_position((panel_x, panel_y))

    def draw(self):
        self.surface.fill(Colors.WHITE)
        self.ui_manager.draw_ui(self.surface)

    def update(self, dt):
        pass

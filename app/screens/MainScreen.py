import cv2
import numpy as np
import pygame
from pygame import Event
from pygame_gui import elements

from app.AppContext import AppContext
from app.common import Colors
from app.custom_elements.ButtonsPanel import ButtonsPanel
from app.custom_elements.StorageBox import StorageBox
from app.custom_elements.Workspace import Workspace
from app.screens.PhysScreen import PhysScreen
from app.screens.base.ScreenBase import ScreenBase
from app.CameraController import CameraController, ActionState
from packing_lib.packing_lib.packers.NFDHPacker import NFDHPacker
from packing_lib.packing_lib.types import PackingInputTask, PackingContainer, PackInputObject, PlacedObject


class MainScreen(ScreenBase):
    def __init__(self, context: AppContext):
        super().__init__(context)

        self._init_ui_elements()

        self.cam_fixed = False

        self.camera_controller: CameraController = self.context.camera_controller
        self.camera_controller.on_camera_connected.append(self._on_camera_connected)

    def _init_ui_elements(self):
        self.workspace = Workspace(pygame.Rect(0, 0, 0, 0))
        self.message_box = elements.UITextBox(
            html_text='',
            relative_rect=pygame.Rect(0, 0, 0, 0),
            manager=self.context.ui_manager
        )
        self.storage_box = StorageBox(self.config.box_width, self.config.box_height)
        self.buttons_panel = ButtonsPanel(pygame.Rect(0, 0, 200, 0), self.context.ui_manager)

        self.update_layout(self.context.surface.size)

    def update_layout(self, size):
        screen_w, screen_h = size
        margin = 30
        gap = 20
        panel_width = self.buttons_panel.rect.w
        divider_width = 2

        total_gap = gap * 2
        usable_width = screen_w - margin * 2 - panel_width - total_gap

        box_width = usable_width // 2

        workspace_height = box_width * self.workspace.camera_resolution_ratio
        new_workspace = pygame.Rect(margin, (screen_h - workspace_height) // 2, box_width, workspace_height)
        self.workspace.update_rect(new_workspace)

        message_margin_top = 10
        message_height = 60
        message_width = self.workspace.rect.width

        message_x = self.workspace.rect.x
        message_y = self.workspace.rect.bottom + message_margin_top

        self.message_box.set_relative_position((message_x, message_y))
        self.message_box.set_dimensions((message_width, message_height))

        storage_width = self.config.box_width * 1000
        storage_height = storage_width * self.storage_box.aspect_ratio
        new_storage = pygame.Rect(new_workspace.right + gap, (screen_h - storage_height) // 2,
                                  storage_width, storage_height)
        self.storage_box.update_rect(new_storage)

        new_buttons = pygame.Rect(new_workspace.right + gap + box_width + gap, 0, panel_width, screen_h)
        self.buttons_panel.rect.update(new_buttons)
        self.buttons_panel.update_layout()

        self._dividers = [
            (new_workspace.x + box_width + gap // 2, 0, divider_width, screen_h),  # между Workspace и Storage
            (new_storage.x + box_width + gap // 2, 0, divider_width, screen_h)  # между Storage и кнопками
        ]

    def handle_resize(self, new_size):
        self.update_layout(new_size)

    def update(self, dt):
        self.message_box.set_text(self.camera_controller.connection_status)

        cam_button_message = (
            "включить камеру" if self.camera_controller.capturing == ActionState.STOPPED else
            "выключить камеру" if self.camera_controller.capturing == ActionState.STARTED else
            "подождите.."
        )
        process_button_message = (
            "начать обработку" if self.camera_controller.processing == ActionState.STOPPED else
            "остановить обработку" if self.camera_controller.processing == ActionState.STARTED else
            "подождите.."
        )
        fix_cam_button_message = "Отпустить" if self.cam_fixed else "Зафиксировать"

        self.buttons_panel.camera_button.set_text(cam_button_message)
        self.buttons_panel.process_button.set_text(process_button_message)
        self.buttons_panel.fix_cam_button.set_text(fix_cam_button_message)

        if self.camera_controller.capturing == ActionState.STARTED:
            self.buttons_panel.process_button.enable()
        else:
            self.buttons_panel.process_button.disable()

        if self.camera_controller.processing == ActionState.STARTED:
            self.buttons_panel.fix_cam_button.enable()
        else:
            self.buttons_panel.fix_cam_button.disable()

        if self.cam_fixed:
            return

        self.workspace.camera_frame = self.camera_controller.get_frame()

        if self.camera_controller.processing.STARTED:
            self.update_camera_process_result()

    def update_camera_process_result(self):
        boxes = self.camera_controller.get_boxes()
        self.workspace.boxes = boxes
        aruco_markers = self.camera_controller.get_markers()
        self.workspace.detected_markers = aruco_markers

    @staticmethod
    def cut_rect(frame, rect):
        center = rect[0]
        size = rect[1]
        angle = rect[2]

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(frame, rotation_matrix, (frame.shape[1], frame.shape[0]))

        w, h = size
        cropped = cv2.getRectSubPix(rotated, (int(w), int(h)), center)
        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        cropped_rgb = np.rot90(cropped_rgb)
        return cropped_rgb

    def draw(self):
        self.surface.fill(Colors.WHITE)
        self.storage_box.draw(self.surface)
        self.workspace.draw(self.surface)
        self.buttons_panel.draw(self.surface)
        self.draw_dividers(self.surface)

    def draw_dividers(self, surface):
        divider_color = (180, 180, 180)
        for x, y, w, h in getattr(self, '_dividers', []):
            pygame.draw.rect(surface, divider_color, pygame.Rect(x, y, w, h))

    def handle_event(self, event: Event):
        if event.ui_element == self.buttons_panel.gen_button:
            self.workspace.create_random_items(10)
        elif event.ui_element == self.buttons_panel.place_button:
            self.place_to_box()
        elif event.ui_element == self.buttons_panel.place_phys_button:
            self.place_phys()

        elif event.ui_element == self.buttons_panel.camera_button:
            self.cam_fixed = False
            if self.camera_controller.capturing == ActionState.STOPPED:
                self.camera_controller.start()
            elif self.camera_controller.capturing == ActionState.STARTED:
                self.camera_controller.stop()

        elif event.ui_element == self.buttons_panel.process_button:
            if self.camera_controller.processing == ActionState.STOPPED:
                self.camera_controller.start_processing()
            elif self.camera_controller.processing == ActionState.STARTED:
                self.camera_controller.stop_processing()

        elif event.ui_element == self.buttons_panel.fix_cam_button:
            self.fix_cam()

    def fix_cam(self):
        self.cam_fixed = not self.cam_fixed
        if not self.cam_fixed:
            self.workspace.detected_boxes = []
        else:
            boxes = [cv2.minAreaRect(box) for box in self.workspace.boxes]
            self.workspace.detected_boxes = [
                DrawableRect(pygame.Rect(x, y, w, h), angle,
                             self.cut_rect(self.workspace.camera_frame, ((x, y), (w, h), angle)))
                for ((x, y), (w, h), angle) in boxes]

            self.workspace.generated_boxes = []

    def place_to_box(self):
        packer = NFDHPacker()
        boxes_to_pack = self.workspace.detected_boxes if len(self.workspace.detected_boxes) > 0 \
            else self.workspace.generated_boxes
        pack_objects = [
            PackInputObject(
                id=i,
                width=box.rect.w,
                height=box.rect.h
            ) for i, box in enumerate(boxes_to_pack)
        ]
        task = PackingInputTask(
            PackingContainer(*self.storage_box.rect.size),
            pack_objects
        )

        result = packer.pack(task)
        self.storage_box.placeables = [DrawableRect(pygame.Rect(int(obj.left), int(obj.top), int(obj.width), int(obj.height))) for obj in
                                       result]


    def place_phys(self):
        self.screen_manager.switch_to(PhysScreen, self.config.box_width, self.config.box_height,
                                      self.workspace.generated_boxes)

    # def _on_packing_completed(self, packed):
    #     self.storage_box.placeables = packed

    def _on_camera_connected(self):
        resolution = self.camera_controller.get_camera_resolution()
        if resolution is not None:
            self.workspace.set_camera_resolution(*resolution)
            self.update_layout(self.surface.size)

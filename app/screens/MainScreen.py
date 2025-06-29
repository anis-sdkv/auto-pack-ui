import pygame
from pygame import Event
from pygame_gui import elements

from app.AppContext import AppContext
from app.common import Colors
from app.custom_elements.ButtonsPanel import ButtonsPanel
from app.custom_elements.StorageBox import StorageBox
from app.custom_elements.Workspace import Workspace
from app.screens.ConfigScreen import ConfigScreen
from app.screens.base.ScreenBase import ScreenBase
from app.CameraController import CameraController, ActionState
from app.PackingTaskManager import PackingTaskManager, PackingTask, TaskStatus
from app.MainScreenState import main_screen_state
from packing_lib.packing_lib.packers.NFDHPacker import NFDHPacker
from packing_lib.packing_lib.types import PackingInputTask, PackingContainer, PackInputObject


class MainScreen(ScreenBase):
    def __init__(self, context: AppContext):
        super().__init__(context)

        self._init_ui_elements()

        self.cam_fixed = False

        self.camera_controller: CameraController = self.context.camera_controller
        self.camera_controller.on_camera_connected.append(self._on_camera_connected)

        # Менеджер фоновых задач упаковки
        self.task_manager = PackingTaskManager()
        self.task_manager.add_status_callback(self._on_task_status_changed)
        self.task_manager.add_completion_callback(self._on_task_completed)

    def _init_ui_elements(self):
        self.workspace = Workspace(pygame.Rect(0, 0, 0, 0))
        self.message_box = elements.UITextBox(
            html_text='',
            relative_rect=pygame.Rect(0, 0, 0, 0),
            manager=self.context.ui_manager
        )
        self.status_box = elements.UITextBox(
            html_text='Готов к упаковке',
            relative_rect=pygame.Rect(0, 0, 0, 0),
            manager=self.context.ui_manager
        )
        self.storage_box = StorageBox(self.config.box_width, self.config.box_height)
        self.buttons_panel = ButtonsPanel(pygame.Rect(0, 0, 200, 0), self.context.ui_manager)

        self.update_layout(self.context.surface.size)

    def on_show(self):
        """Вызывается при переходе на этот экран"""
        # Пересоздаем все UI элементы (они были удалены при clear_and_reset)
        self._init_ui_elements()

        # Восстанавливаем состояние из глобального хранилища
        self._restore_state_from_storage()

        self.update_layout(self.context.surface.size)

    def _save_state_to_storage(self):
        """Сохраняет текущее состояние в глобальное хранилище"""
        # Сохраняем объекты из storage_box
        if hasattr(self, 'storage_box') and self.storage_box:
            main_screen_state.set_storage_objects(getattr(self.storage_box, 'objects', []))
        
        # Сохраняем состояние камеры включая resolution
        main_screen_state.save_camera_state(
            self.cam_fixed,
            getattr(self.workspace, 'detected_boxes', []),
            getattr(self.workspace, 'generated_boxes', []),
            getattr(self.workspace, 'camera_frame', None),
            getattr(self.workspace, 'camera_width', None),
            getattr(self.workspace, 'camera_resolution_ratio', 1.0)
        )

    def _restore_state_from_storage(self):
        """Восстанавливает состояние из глобального хранилища"""
        # Восстанавливаем объекты в storage_box
        if main_screen_state.storage_objects:
            self.storage_box.set_objects(main_screen_state.storage_objects)
        
        # Применяем отложенный результат физической упаковки если есть
        if main_screen_state.apply_physics_result():
            self.storage_box.set_objects(main_screen_state.storage_objects)
        
        # Восстанавливаем camera resolution ПЕРВЫМ - это критично для правильного масштабирования
        if main_screen_state.camera_width is not None:
            self.workspace.set_camera_resolution(main_screen_state.camera_width, 
                                               int(main_screen_state.camera_width * main_screen_state.camera_resolution_ratio))
        
        # Восстанавливаем состояние камеры
        self.cam_fixed = main_screen_state.cam_fixed
        if main_screen_state.detected_boxes:
            self.workspace.detected_boxes = main_screen_state.detected_boxes
        if main_screen_state.generated_boxes:
            self.workspace.generated_boxes = main_screen_state.generated_boxes
        if main_screen_state.camera_frame is not None:
            self.workspace.camera_frame = main_screen_state.camera_frame
        
        # Устанавливаем статус
        try:
            self.status_box.set_text(main_screen_state.status_message)
        except Exception as e:
            print(f"Error setting status text: {e}")

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

        # StorageBox занимает всю доступную ширину с сохранением aspect ratio
        storage_width = box_width
        storage_height = storage_width * self.storage_box.aspect_ratio

        # Если не помещается по высоте, масштабируем по высоте
        max_height = screen_h - 2 * margin
        if storage_height > max_height:
            storage_height = max_height
            storage_width = storage_height / self.storage_box.aspect_ratio

        new_storage = pygame.Rect(new_workspace.right + gap, (screen_h - storage_height) // 2,
                                  int(storage_width), int(storage_height))
        self.storage_box.update_rect(new_storage)

        # Status box под storage_box (аналогично message_box под workspace)
        status_margin_top = 10
        status_height = 60
        status_width = new_storage.width
        status_x = new_storage.x
        status_y = new_storage.bottom + status_margin_top

        self.status_box.set_relative_position((status_x, status_y))
        self.status_box.set_dimensions((status_width, status_height))

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

        # Проверяем результаты фоновых задач
        self.task_manager.check_results()

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

        # Управляем видимостью кнопки отмены
        status, _ = self.task_manager.get_current_status()
        if status == TaskStatus.RUNNING:
            self.buttons_panel.cancel_button.show()
            # Блокируем кнопки упаковки
            self.buttons_panel.place_button.disable()
            self.buttons_panel.place_phys_button.disable()
            self.buttons_panel.place_exact_button.disable()
        else:
            self.buttons_panel.cancel_button.hide()
            # Разблокируем кнопки упаковки
            self.buttons_panel.place_button.enable()
            self.buttons_panel.place_phys_button.enable()
            self.buttons_panel.place_exact_button.enable()

        if self.camera_controller.capturing == ActionState.STARTED:
            self.buttons_panel.process_button.enable()
        else:
            self.buttons_panel.process_button.disable()

        if (self.camera_controller.processing == ActionState.STARTED and
                self.camera_controller.get_calibration_status()):
            self.buttons_panel.fix_cam_button.enable()
        elif self.cam_fixed:
            self.buttons_panel.fix_cam_button.enable()
        else:
            self.buttons_panel.fix_cam_button.disable()

        # СНАЧАЛА проверяем фиксацию - если зафиксировано, НЕ обновляем кадр
        if self.cam_fixed:
            return

        # ТОЛЬКО если НЕ зафиксировано - обновляем кадр и результаты обработки
        self.workspace.camera_frame = self.camera_controller.get_frame()

        if self.camera_controller.processing.STARTED:
            self.update_camera_process_result()

    def update_camera_process_result(self):
        boxes = self.camera_controller.get_boxes()
        self.workspace.boxes = boxes
        aruco_markers = self.camera_controller.get_markers()
        self.workspace.detected_markers = aruco_markers
        calibration_status = self.camera_controller.get_calibration_status()
        self.workspace.is_calibrated = calibration_status

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
        elif event.ui_element == self.buttons_panel.place_exact_button:
            self.place_exact()
        elif event.ui_element == self.buttons_panel.cancel_button:
            self.task_manager.cancel_current_task()

        elif event.ui_element == self.buttons_panel.camera_button:
            self.cam_fixed = False
            if self.camera_controller.capturing == ActionState.STOPPED:
                self.workspace.generated_boxes = []
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

        elif event.ui_element == self.buttons_panel.settings_button:
            self.screen_manager.switch_to(ConfigScreen)

    def fix_cam(self):
        if not self.camera_controller.get_calibration_status():
            return
        self.cam_fixed = not self.cam_fixed
        if not self.cam_fixed:
            # Расфиксация - возобновляем capture и запускаем обработку
            self.camera_controller.resume_capture()
            self.camera_controller.start_processing()
            self.workspace.detected_boxes = []
            status_msg = "Готов к упаковке"
            self.status_box.set_text(status_msg)
            main_screen_state.clear_camera_state()
            main_screen_state.status_message = status_msg
        else:
            # Фиксация - сохраняем состояние и полностью останавливаем камеру
            converted_boxes = self.camera_controller.get_converted_boxes()
            current_frame = self.camera_controller.get_frame()
            
            self.workspace.detected_boxes = converted_boxes
            self.workspace.generated_boxes = []
            # Фиксируем текущий кадр в workspace
            self.workspace.camera_frame = current_frame
            
            # Останавливаем обработку и приостанавливаем capture
            self.camera_controller.stop_processing()
            self.camera_controller.pause_capture()
            
            status_msg = f"Готов к упаковке ({len(converted_boxes)} объектов распознано)"
            self.status_box.set_text(status_msg)
            
            # Сохраняем состояние с зафиксированным кадром
            main_screen_state.save_camera_state(
                self.cam_fixed,
                converted_boxes,
                [],
                current_frame,
                getattr(self.workspace, 'camera_width', None),
                getattr(self.workspace, 'camera_resolution_ratio', 1.0)
            )
            main_screen_state.status_message = status_msg

    def place_to_box(self):
        task_data = self._prepare_packing_task()
        if not task_data:
            return

        def nfdh_packer_func(task_data, cancel_event):
            packer = NFDHPacker()
            return packer.pack(task_data, cancel_event)

        task = PackingTask("nfdh", "NFDH упаковка", nfdh_packer_func, task_data)
        self.task_manager.start_task(task)

    def place_phys(self):
        task_data = self._prepare_packing_task()
        if not task_data:
            return

        # Сохраняем текущее состояние в глобальное хранилище
        self._save_state_to_storage()

        # Переходим на экран визуализации
        from app.screens.PhysVisualizationScreen import PhysVisualizationScreen
        self.screen_manager.switch_to(PhysVisualizationScreen, task_data)

    def place_exact(self):
        task_data = self._prepare_packing_task()
        if not task_data:
            return

        def exact_packer_func(task_data, cancel_event):
            from packing_lib.packing_lib.packers.ExactORToolsPacker import ExactORToolsPacker
            packer = ExactORToolsPacker(time_limit_seconds=60, allow_rotation=True)
            return packer.pack(task_data, cancel_event)

        task = PackingTask("exact", "Точная упаковка", exact_packer_func, task_data)
        self.task_manager.start_task(task)

    def _prepare_packing_task(self) -> PackingInputTask:
        """Подготавливает данные для упаковки"""
        pack_objects = []

        # Приоритет: зафиксированные объекты камеры, затем сгенерированные
        if self.cam_fixed and self.workspace.detected_boxes:
            pack_objects = [
                PackInputObject(
                    id=obj.id,
                    width=obj.width,
                    height=obj.height
                ) for obj in self.workspace.detected_boxes
            ]
        elif self.workspace.generated_boxes:
            # Fallback для сгенерированных объектов
            pack_objects = [
                PackInputObject(
                    id=i,
                    width=rect.w,
                    height=rect.h
                ) for i, (rect, color) in enumerate(self.workspace.generated_boxes)
            ]

        if not pack_objects:
            self.status_box.set_text("Нет объектов для упаковки")
            return None

        return PackingInputTask(
            PackingContainer(self.config.box_width, self.config.box_height),
            pack_objects
        )

    # def _on_packing_completed(self, packed):
    #     self.storage_box.placeables = packed

    def _on_camera_connected(self):
        resolution = self.camera_controller.get_camera_resolution()
        if resolution is not None:
            self.workspace.set_camera_resolution(*resolution)
            # Сохраняем camera resolution в глобальное состояние
            main_screen_state.set_camera_resolution(*resolution)
            self.update_layout(self.surface.size)

    def _on_task_status_changed(self, status: TaskStatus, task_name: str):
        """Обновляет UI при смене статуса задачи"""
        if status == TaskStatus.RUNNING:
            self.status_box.set_text(f"Выполняется: {task_name}...")
        elif status == TaskStatus.CANCELLED:
            self.status_box.set_text("Задача отменена")
        else:
            self.status_box.set_text("Готов к упаковке")

    def _on_task_completed(self, task: PackingTask):
        """Обрабатывает завершение задачи"""
        try:
            if task.status == TaskStatus.COMPLETED and task.result:
                self.storage_box.set_objects(task.result)
                main_screen_state.set_storage_objects(task.result)
                status_msg = f"{task.name} завершена: {len(task.result)} объектов размещено"
                self.status_box.set_text(status_msg)
                main_screen_state.status_message = status_msg
            elif task.status == TaskStatus.ERROR:
                status_msg = f"Ошибка в {task.name}: {task.error}"
                self.status_box.set_text(status_msg)
                main_screen_state.status_message = status_msg
            elif task.status == TaskStatus.CANCELLED:
                status_msg = f"{task.name} отменена"
                self.status_box.set_text(status_msg)
                main_screen_state.status_message = status_msg
        except pygame.error as e:
            print(f"Font rendering error: {e}")

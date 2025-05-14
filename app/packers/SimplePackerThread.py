import threading
import time

import pygame


class SimplePackerThread(threading.Thread):
    def __init__(self, screen_model):
        super().__init__()
        self.screen_model = screen_model
        self.bin_width = self.screen_model.storage_box.width
        self.bin_height = self.screen_model.storage_box.height
        self.x_cursor = 0
        self.y_cursor = 0

    def run(self):
        self._animate()

    def _get_rectangles_to_pack(self):
        row_height = 0

        for rect in self.screen_model.workspace.detected_boxes:
            # Если не помещается по ширине — переносим на новую строку
            if self.x_cursor + rect.width > self.bin_width:
                self.x_cursor = 0
                self.y_cursor += row_height
                row_height = 0

            # Если не помещается по высоте — всё, конец
            if self.y_cursor + rect.height > self.bin_height:
                print(f"⚠️ Rectangle {rect} не помещается")
                yield rect, None
                continue

            yield rect, (self.x_cursor, self.y_cursor)

            # Сдвигаем курсор
            self.x_cursor += rect.width
            row_height = max(row_height, rect.height)

    def _animate(self):
        for rect, target_cords in self._get_rectangles_to_pack():

            if target_cords is None:
                original_color = rect.back_color
                rect.back_color = (255, 0, 0)
                time.sleep(0.3)
                rect.back_color = original_color
                continue

            self.screen_model.storage_box.detected_boxes.append(rect)

            start_x, start_y = rect.x, rect.y
            target_x, target_y = self.screen_model.storage_box.x + target_cords[0], self.screen_model.storage_box.y + \
                                 target_cords[1]

            steps = 10
            for step in range(steps + 1):
                rect.x = start_x + (target_x - start_x) * step / steps
                rect.y = start_y + (target_y - start_y) * step / steps

                time.sleep(0.01)

        self.screen_model.workspace.detected_boxes = [i for i in self.screen_model.workspace.detected_boxes if
                                                      not i in self.screen_model.storage_box.detected_boxes]

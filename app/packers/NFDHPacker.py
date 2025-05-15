import threading
from typing import List

import pygame

from app.custom_elements.DrawableRect import DrawableRect


class NFDHPacker:
    def __init__(self, bin_width: int, bin_height: int):
        self.bin_width = bin_width
        self.bin_height = bin_height

        self.result = None

    def start(self, source_rects: List[DrawableRect], on_complete):
        self.result = None
        packer_thread = threading.Thread(target=self.pack, args=(source_rects, on_complete), daemon=True)
        packer_thread.start()

    def pack(self, source_rects: List[DrawableRect], on_complete):
        source_rects = [(r.rect_id, r.rect, r.image) for r in source_rects]
        source_rects = sorted(source_rects, key=lambda r: r[1].height, reverse=True)

        packed = []

        x_cursor = 0
        y_cursor = 0
        current_row_height = 0

        for rect_id, rect, image in source_rects:
            if rect.width > self.bin_width or rect.height > self.bin_height:
                continue

            if x_cursor + rect.width > self.bin_width:
                y_cursor += current_row_height
                x_cursor = 0
                current_row_height = 0

            if y_cursor + rect.height > self.bin_height:
                continue

            packed.append(DrawableRect(pygame.Rect(x_cursor, y_cursor, rect.width, rect.height), rect_id=rect_id, image=image))

            x_cursor += rect.width
            current_row_height = max(current_row_height, rect.height)

        on_complete(packed)

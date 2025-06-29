from typing import List
from ..interfaces.BasePacker import BasePacker
from ..types import PackingInputTask, PlacedObject


class NFDHPacker(BasePacker):
    def pack(self, task: PackingInputTask) -> List[PlacedObject]:
        objects = sorted(task.objects, key=lambda r: r.height, reverse=True)

        packed = []
        x_cursor = 0
        y_cursor = 0
        current_row_height = 0

        for obj in objects:
            if obj.width > task.container.width or obj.height > task.container.height:
                continue

            if x_cursor + obj.width > task.container.width:
                y_cursor += current_row_height
                x_cursor = 0
                current_row_height = 0

            if y_cursor + obj.height > task.container.height:
                continue

            center_x = x_cursor + obj.width / 2
            center_y = y_cursor + obj.height / 2
            
            packed.append(PlacedObject(
                id=obj.id,
                center_x=center_x,
                center_y=center_y,
                width=obj.width,
                height=obj.height,
            ))

            x_cursor += obj.width
            current_row_height = max(current_row_height, obj.height)

        return packed

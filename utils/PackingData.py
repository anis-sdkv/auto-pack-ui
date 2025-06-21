import json
import os

# from app.custom_elements.DrawableRect import DrawableRect


class PackingData:
    def __init__(self, box_width, box_height):
        self.box_width = box_width
        self.box_height = box_height
        self.objects = []  # список объектов (x, y, w, h)

    def clear(self):
        self.objects = []

    def add_objects(self, drawables: list[DrawableRect]):
        rects = [i.rect for i in drawables]
        for (x, y, w, h) in rects:
            self.objects.append({
                'x': x,
                'y': y,
                'w': w,
                'h': h
            })

    def add_object(self, x, y, w, h):
        self.objects.append({
            'x': x,
            'y': y,
            'w': w,
            'h': h
        })

    def save_to_file(self, path):
        data = {
            'box_width': self.box_width,
            'box_height': self.box_height,
            'objects': self.objects
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_from_file(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        packing_data = PackingData(data['box_width'], data['box_height'])
        packing_data.objects = data['objects']
        return packing_data

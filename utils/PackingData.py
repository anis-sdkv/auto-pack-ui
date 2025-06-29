import json
import os
from typing import List
from packing_lib.packing_lib.types import PlacedObject


class PackingData:
    def __init__(self, box_width: float, box_height: float):
        self.box_width = box_width
        self.box_height = box_height
        self.objects: List[dict] = []  # список объектов в формате словарей

    def clear(self):
        self.objects.clear()

    def add_objects(self, placed_objects: List[PlacedObject]):
        for obj in placed_objects:
            self.objects.append({
                'id': int(obj.id),  # конвертируем в Python native int
                'x': float(obj.left),  # конвертируем NumPy типы в Python native float
                'y': float(obj.top),   
                'w': float(obj.width),
                'h': float(obj.height)
            })

    def add_object(self, obj: PlacedObject):
        self.objects.append({
            'id': int(obj.id),  # конвертируем в Python native int
            'x': float(obj.left),  # конвертируем NumPy типы в Python native float
            'y': float(obj.top),   
            'w': float(obj.width),
            'h': float(obj.height)
        })

    def save_to_file(self, path: str):
        data = {
            'box_width': float(self.box_width),  # конвертируем NumPy типы в Python native
            'box_height': float(self.box_height),
            'objects': self.objects
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_from_file(filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
        packing_data = PackingData(data['box_width'], data['box_height'])
        packing_data.objects = data['objects']
        return packing_data

from utils.PackingDataV2 import PackingDataV2


class PlacementDensityCalculator:
    def __init__(self, data: PackingDataV2):
        self.box_width = data.box_width
        self.box_height = data.box_height
        self.objects = data.objects

    def calculate_total_object_area(self):
        total_area = 0
        for obj in self.objects:
            obj_area = obj['w'] * obj['h']
            total_area += obj_area
        return total_area

    def calculate_box_area(self):
        return self.box_width * self.box_height

    def calculate_density(self):
        object_area = self.calculate_total_object_area()
        box_area = self.calculate_box_area()
        density = object_area / box_area if box_area > 0 else 0
        return density
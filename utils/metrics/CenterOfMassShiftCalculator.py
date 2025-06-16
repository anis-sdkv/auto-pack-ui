import math


class CenterOfMassShiftCalculator:
    def __init__(self, data):
        self.box_width = data.box_width
        self.box_height = data.box_height
        self.objects = data.objects

    def calculate_center_of_mass_objects(self):
        sum_Ai_xi = 0
        sum_Ai_yi = 0
        sum_Ai = 0
        for obj in self.objects:
            Ai = obj['w'] * obj['h']
            xi = obj['x'] + obj['w'] / 2  # центр объекта по x
            yi = obj['y'] + obj['h'] / 2  # центр объекта по y
            sum_Ai_xi += Ai * xi
            sum_Ai_yi += Ai * yi
            sum_Ai += Ai

        if sum_Ai == 0:
            return (0, 0)

        Cx = sum_Ai_xi / sum_Ai
        Cy = sum_Ai_yi / sum_Ai

        return (Cx, Cy)

    def calculate_center_of_mass_container(self):
        # Центр прямоугольника по оси X и Y
        return (self.box_width / 2, self.box_height / 2)

    def calculate_shift(self):
        Cx_obj, Cy_obj = self.calculate_center_of_mass_objects()
        Cx0, Cy0 = self.calculate_center_of_mass_container()
        shift = math.sqrt((Cx_obj - Cx0) ** 2 + (Cy_obj - Cy0) ** 2)
        half_diagonal = math.sqrt(self.box_width ** 2 + self.box_height ** 2) / 2

        if half_diagonal == 0:
            return 0

        normalized_shift = shift / half_diagonal
        return normalized_shift

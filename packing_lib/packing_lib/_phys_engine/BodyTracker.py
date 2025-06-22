import pymunk


class BodyTracker:
    def __init__(self, body, pos_threshold=3.0, angle_threshold=0.03):
        self.body = body
        self.prev_pos = body.position
        self.prev_angle = body.angle
        self.pos_threshold = pos_threshold
        self.angle_threshold = angle_threshold

    def pos_delta(self):
        return (self.body.position - self.prev_pos).length

    def angle_delta(self):
        return abs(self.body.angle - self.prev_angle)

    def is_stationary(self):
        return self.pos_delta() < self.pos_threshold and self.angle_delta() < self.angle_threshold

    def update(self):
        self.prev_pos = self.body.position
        self.prev_angle = self.body.angle

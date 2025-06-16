import pymunk


class BodyTracker:
    def __init__(self, body):
        self.body = body
        self.prev_pos = body.position
        self.prev_angle = body.angle

    def pos_delta(self):
        return (self.body.position - self.prev_pos).length

    def angle_delta(self):
        return abs(self.body.angle - self.prev_angle)

    def is_stationary(self, pos_threshold=3, angle_threshold=0.03):
        return self.pos_delta() < pos_threshold and self.angle_delta() < angle_threshold

    def update(self):
        self.prev_pos = self.body.position
        self.prev_angle = self.body.angle

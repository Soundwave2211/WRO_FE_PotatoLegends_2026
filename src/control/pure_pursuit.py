import math

class PurePursuit:
    def __init__(self, lookahead=0.35, wheelbase=0.18, max_steer_deg=28):
        self.lookahead = lookahead
        self.wheelbase = wheelbase
        self.max_steer_deg = max_steer_deg
        self.index = 0

    def reset(self):
        self.index = 0

    @property
    def current_index(self):
        return self.index
    
    def update(self, pose, path):
        x, y, theta = pose
        self.index = self.nearest_index(x, y, path)
        target = self.lookahead_point(path)
        tx, ty = target
        dx = tx - x
        dy = ty - y
        target_angle = math.atan2(dy, dx)
        alpha = target_angle - theta
        alpha = math.atan2(math.sin(alpha), math.cos(alpha))
        steer_rad = math.atan2(
            2 * self.wheelbase * math.sin(alpha),
            self.lookahead
        )
        steer_deg = math.degrees(steer_rad)
        steer_deg = max(-self.max_steer_deg, min(self.max_steer_deg, steer_deg))
        return steer_deg, target

    def nearest_index(self, x, y, path):
        best_i = self.index
        best_d = 999999
        for i in range(self.index, min(self.index + 80, len(path))):
            px, py = path[i]
            d = math.hypot(px - x, py - y)
            if d < best_d:
                best_d = d
                best_i = i
        return best_i

    def lookahead_point(self, path):
        target_i = min(self.index + 12, len(path) - 1)
        return path[target_i]

    def finished(self, path):
        return self.index >= len(path) - 20
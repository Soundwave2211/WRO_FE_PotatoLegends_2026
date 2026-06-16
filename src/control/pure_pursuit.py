import math

class PurePursuit:
    def __init__(self, wheelbase=0.18, lookahead=0.42, max_steer_deg=28):
        self.L = wheelbase
        self.lookahead = lookahead
        self.max_steer_deg = max_steer_deg
        self.index = 0
        self.nearest_point = (0.0, 0.0)
        self.target_point = (0.0, 0.0)
        self.cross_track_error = 0.0
        self.heading_error = 0.0

    def reset(self):
        self.index = 0
        self.nearest_point = (0.0, 0.0)
        self.target_point = (0.0, 0.0)
        self.cross_track_error = 0.0
        self.heading_error = 0.0

    def update(self, pose, path, closed=True):
        x, y, theta = pose

        if len(path) < 2:
            return 0.0, 0.0, (x, y)
        self.index = self.find_nearest_index(x, y, path, closed)
        target_i = self.find_lookahead_index(path, closed)
        nearest = path[self.index]
        target = path[target_i]
        self.nearest_point = nearest
        self.target_point = target
        self.cross_track_error = math.hypot(x - nearest[0], y - nearest[1])
        tx, ty = target
        angle_to_target = math.atan2(ty - y, tx - x)
        alpha = self.norm_angle(angle_to_target - theta)
        self.heading_error = alpha
        steer_rad = math.atan2(2 * self.L * math.sin(alpha), self.lookahead)
        steer_deg = math.degrees(steer_rad)
        steer_deg = max(-self.max_steer_deg, min(self.max_steer_deg, steer_deg))
        speed = self.speed_from_steer(steer_deg)
        return steer_deg, speed, target

    def find_nearest_index(self, x, y, path, closed=True):
        best_i = self.index
        best_d = 999999
        if closed:
            search_range = range(len(path))
        else:
            search_range = range(self.index, len(path))

        for i in search_range:
            px, py = path[i]
            d = math.hypot(px - x, py - y)

            if d < best_d:
                best_d = d
                best_i = i
        return best_i

    def find_lookahead_index(self, path, closed=True):
        distance = 0.0
        i = self.index
        for _ in range(len(path)):
            if not closed and i >= len(path) - 1:
                return len(path) - 1

            p1 = path[i % len(path)]
            p2 = path[(i + 1) % len(path)]
            distance += math.hypot(p2[0] - p1[0], p2[1] - p1[1])

            if distance >= self.lookahead:
                if closed:
                    return (i + 1) % len(path)
                return min(i + 1, len(path) - 1)
            i += 1
        return self.index

    def speed_from_steer(self, steer_deg):
        a = abs(steer_deg)
        if a > 23:
            return 0.16
        if a > 15:
            return 0.24
        if a > 8:
            return 0.32
        return 0.42

    def norm_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))
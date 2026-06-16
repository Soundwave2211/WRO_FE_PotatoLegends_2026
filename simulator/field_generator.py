import random

class WROField:
    def __init__(self, seed=1):
        random.seed(seed)
        self.outer_w = 4.0
        self.outer_h = 3.0
        self.inner_w = random.choice([1.7, 1.9, 2.1])
        self.inner_h = random.choice([0.9, 1.1, 1.3])
        self.outer = self.rect(self.outer_w, self.outer_h)
        self.inner = self.rect(self.inner_w, self.inner_h)
        self.signs = self.make_signs()
        self.parking = {
            "x": -1.55,
            "y": 0.65,
            "w": 0.45,
            "h": 0.75,
        }

    def rect(self, w, h):
        return [
            (-w / 2, -h / 2),
            (w / 2, -h / 2),
            (w / 2, h / 2),
            (-w / 2, h / 2),
            (-w / 2, -h / 2),
        ]

    def centre_path(self, points_per_side=90):
        a = (self.outer_w / 2 + self.inner_w / 2) / 2
        b = (self.outer_h / 2 + self.inner_h / 2) / 2
        path = []

        for i in range(points_per_side):
            t = i / points_per_side
            path.append((-a + 2 * a * t, -b))

        for i in range(points_per_side):
            t = i / points_per_side
            path.append((a, -b + 2 * b * t))

        for i in range(points_per_side):
            t = i / points_per_side
            path.append((a - 2 * a * t, b))

        for i in range(points_per_side):
            t = i / points_per_side
            path.append((-a, b - 2 * b * t))
        return path

    def make_signs(self):
        base = self.centre_path(90)
        idxs = [45, 135, 225, 315]
        colours = ["red", "green", "red", "green"]
        signs = []

        for idx, colour in zip(idxs, colours):
            x, y = base[idx]
            signs.append({
                "x": x,
                "y": y,
                "colour": colour,
                "r": 0.09,
            })
        return signs

    def inside_track_bounds(self, x, y, margin=0.08):
        inside_outer = (
            abs(x) < self.outer_w / 2 - margin
            and abs(y) < self.outer_h / 2 - margin
        )
        outside_inner = not (
            abs(x) < self.inner_w / 2 + margin
            and abs(y) < self.inner_h / 2 + margin
        )
        return inside_outer and outside_inner

    def hits_sign(self, x, y, radius=0.13):
        for sign in self.signs:
            dx = x - sign["x"]
            dy = y - sign["y"]
            if (dx * dx + dy * dy) ** 0.5 < radius:
                return True
        return False
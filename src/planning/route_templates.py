import math

def oval_route(points_per_lap=220):
    path = []
    a = 1.55
    b = 1.05
    for i in range(points_per_lap):
        t = 2 * math.pi * i / points_per_lap
        x = a * math.cos(t)
        y = b * math.sin(t)
        path.append((x, y))
    return path

def make_lap_route(laps=3):
    one_lap = oval_route()
    path = []
    for _ in range(laps):
        path.extend(one_lap)
    return path
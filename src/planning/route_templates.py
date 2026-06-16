import math
from src.planning.waypoint_generator import resample_closed
from src.planning.waypoint_generator import resample_open
from src.planning.waypoint_generator import smooth_closed
from src.planning.waypoint_generator import smooth_open
from src.planning.waypoint_generator import normal_at

def open_route(field):
    raw = field.centre_path(points_per_side=90)
    path = resample_closed(raw, spacing=0.045)
    path = smooth_closed(path, passes=5)
    safe = []
    for x, y in path:
        if field.inside_track_bounds(x, y, margin=0.08):
            safe.append((x, y))
    return safe

def obstacle_route(field):
    base = open_route(field)
    shifted = []
    for i, (x, y) in enumerate(base):
        nx, ny = normal_at(base, i)
        offset = 0.0
        for sign in field.signs:
            d = math.hypot(x - sign["x"], y - sign["y"])
            if d < 0.55:
                strength = (0.55 - d) / 0.55
                if sign["colour"] == "red":
                    offset -= 0.23 * strength
                else:
                    offset += 0.23 * strength
        px = x + nx * offset
        py = y + ny * offset

        if field.inside_track_bounds(px, py, margin=0.10) and not field.hits_sign(px, py, 0.14):
            shifted.append((px, py))
        else:
            shifted.append((x, y))
    return smooth_closed(shifted, passes=5)

def parking_path(field, pose):
    x, y, theta = pose
    p = field.parking
    raw = [
        (x, y),
        (p["x"] + 0.75, p["y"] - 0.35),
        (p["x"] + 0.45, p["y"] - 0.05),
        (p["x"] + 0.18, p["y"] + 0.08),
        (p["x"], p["y"]),
    ]

    path = resample_open(raw, spacing=0.04)
    path = smooth_open(path, passes=3)

    return path
import math

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def resample_closed(path, spacing=0.05):
    if len(path) < 2:
        return path[:]
    out = []

    for i in range(len(path)):
        a = path[i]
        b = path[(i + 1) % len(path)]
        d = dist(a, b)
        steps = max(1, int(d / spacing))
        for s in range(steps):
            t = s / steps
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            out.append((x, y))
    return out

def resample_open(path, spacing=0.05):
    if len(path) < 2:
        return path[:]
    out = [path[0]]
    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]
        d = dist(a, b)
        steps = max(1, int(d / spacing))

        for s in range(1, steps + 1):
            t = s / steps
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            out.append((x, y))
    return out

def smooth_closed(path, passes=5):
    if len(path) < 5:
        return path[:]
    result = path[:]

    for _ in range(passes):
        new = []
        for i in range(len(result)):
            p0 = result[(i - 1) % len(result)]
            p1 = result[i]
            p2 = result[(i + 1) % len(result)]
            x = 0.25 * p0[0] + 0.50 * p1[0] + 0.25 * p2[0]
            y = 0.25 * p0[1] + 0.50 * p1[1] + 0.25 * p2[1]
            new.append((x, y))
        result = new
    return result

def smooth_open(path, passes=3):
    if len(path) < 5:
        return path[:]
    result = path[:]

    for _ in range(passes):
        new = [result[0]]
        for i in range(1, len(result) - 1):
            p0 = result[i - 1]
            p1 = result[i]
            p2 = result[i + 1]
            x = 0.25 * p0[0] + 0.50 * p1[0] + 0.25 * p2[0]
            y = 0.25 * p0[1] + 0.50 * p1[1] + 0.25 * p2[1]
            new.append((x, y))
        new.append(result[-1])
        result = new
    return result

def heading_at(path, index):
    if len(path) < 2:
        return 0.0
    a = path[index % len(path)]
    b = path[(index + 5) % len(path)]
    return math.atan2(b[1] - a[1], b[0] - a[0])

def normal_at(path, index):
    a = path[index % len(path)]
    b = path[(index + 5) % len(path)]
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    d = math.hypot(dx, dy)
    if d == 0:
        return 0.0, 0.0
    tx = dx / d
    ty = dy / d
    return -ty, tx
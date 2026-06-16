import sys
import os
import math
import pygame
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from simulator.ackermann_model import AckermannCar
from src.control.pure_pursuit import PurePursuit
from src.behaviour.state_machine import ChallengeManager

WIDTH = 1120
HEIGHT = 820
SCALE = 190
BG = (245, 245, 245)
BLACK = (20, 20, 20)
GREY = (190, 190, 190)
DARK = (75, 75, 75)
BLUE = (45, 95, 220)
RED = (220, 50, 50)
GREEN = (35, 165, 75)
MAGENTA = (220, 40, 180)
ORANGE = (240, 150, 40)
CYAN = (30, 170, 210)

def world_to_screen(x, y):
    return int(WIDTH / 2 + x * SCALE), int(HEIGHT / 2 - y * SCALE)

def draw_polyline(screen, points, colour, width=2, closed=False):
    if len(points) < 2:
        return
    pts = [world_to_screen(x, y) for x, y in points]
    pygame.draw.lines(screen, colour, closed, pts, width)

def draw_field(screen, field):
    draw_polyline(screen, field.outer, BLACK, 5)
    draw_polyline(screen, field.inner, BLACK, 5)
    for sign in field.signs:
        sx, sy = world_to_screen(sign["x"], sign["y"])
        colour = RED if sign["colour"] == "red" else GREEN
        pygame.draw.circle(screen, colour, (sx, sy), 13)
        pygame.draw.circle(screen, ORANGE, (sx, sy), int(0.55 * SCALE), 1)
    p = field.parking
    px, py = world_to_screen(p["x"], p["y"])
    pygame.draw.rect(screen, MAGENTA, (px - 40, py - 60, 80, 120), 3)

def draw_car(screen, car):
    x, y, theta = car.pose()
    cx, cy = world_to_screen(x, y)
    length = 52
    width = 30
    body = [
        (length / 2, 0),
        (-length / 2, -width / 2),
        (-length / 2, width / 2),
    ]
    pts = []

    for px, py in body:
        rx = px * math.cos(theta) - py * math.sin(theta)
        ry = px * math.sin(theta) + py * math.cos(theta)
        pts.append((cx + rx, cy - ry))
    pygame.draw.polygon(screen, BLUE, pts)
    hx = cx + math.cos(theta) * 55
    hy = cy - math.sin(theta) * 55
    pygame.draw.line(screen, RED, (cx, cy), (hx, hy), 3)

def draw_debug(screen, car, controller):
    x, y, theta = car.pose()
    cx, cy = world_to_screen(x, y)
    pygame.draw.circle(screen, CYAN, (cx, cy), int(controller.lookahead * SCALE), 1)
    nearest_screen = world_to_screen(*controller.nearest_point)
    target_screen = world_to_screen(*controller.target_point)
    pygame.draw.circle(screen, ORANGE, nearest_screen, 8)
    pygame.draw.circle(screen, MAGENTA, target_screen, 9)
    pygame.draw.line(screen, ORANGE, (cx, cy), nearest_screen, 2)
    pygame.draw.line(screen, MAGENTA, (cx, cy), target_screen, 2)

def draw_hud(screen, car, controller, manager, paused, show_path, debug):
    font = pygame.font.SysFont(None, 25)
    lines = [
        f"Mode: {manager.mode.upper()}",
        f"State: {manager.state}",
        f"Laps: {manager.laps.laps}/3",
        f"Speed: {car.speed():.2f} m/s",
        f"Steering: {car.steering_deg():.1f} deg",
        f"Target: ({controller.target_point[0]:.2f}, {controller.target_point[1]:.2f})",
        f"Cross-track error: {controller.cross_track_error:.3f} m",
        f"Heading error: {math.degrees(controller.heading_error):.1f} deg",
        f"Index: {controller.index}",
        f"Paused: {paused}",
        f"Path: {show_path} | Debug: {debug}",
        "SPACE pause | R reset | O open | B obstacle | D debug | P path | N random",
    ]
    y = 20
    for line in lines:
        img = font.render(line, True, BLACK)
        screen.blit(img, (20, y))
        y += 24

def reset_car(car, manager, controller):
    x, y, theta = manager.start_pose()
    car.reset(x, y, theta)
    controller.reset()

def collision_check(car, field, check_signs):
    x, y, _ = car.pose()
    if not field.inside_track_bounds(x, y, margin=0.035):
        return True
    if check_signs and field.hits_sign(x, y, radius=0.13):
        return True
    return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("WRO Future Engineers 2026 Simulator")
    clock = pygame.time.Clock()
    manager = ChallengeManager()
    car = AckermannCar()
    controller = PurePursuit(wheelbase=0.18, lookahead=0.42)
    reset_car(car, manager, controller)
    paused = False
    show_path = True
    debug = True
    trail = []
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    manager.reset_same_mode()
                    reset_car(car, manager, controller)
                    trail = []
                elif event.key == pygame.K_o:
                    manager.load_open()
                    reset_car(car, manager, controller)
                    trail = []
                elif event.key == pygame.K_b:
                    manager.load_obstacle()
                    reset_car(car, manager, controller)
                    trail = []
                elif event.key == pygame.K_n:
                    manager.reset_same_mode(new_seed=True)
                    reset_car(car, manager, controller)
                    trail = []
                elif event.key == pygame.K_d:
                    debug = not debug
                elif event.key == pygame.K_p:
                    show_path = not show_path

        if not paused and manager.state != "COLLISION":
            steer, speed, target = controller.update(
                car.pose(),
                manager.path,
                manager.closed_path,
            )
            manager.update_state(controller.index, car.pose())
            if manager.should_stop():
                speed = 0.0
            car.set_steering(steer)
            car.set_speed(speed)
            car.update(dt)
            if collision_check(car, manager.field, manager.mode == "obstacle"):
                manager.state = "COLLISION"
                car.set_speed(0.0)
        x, y, _ = car.pose()
        trail.append(world_to_screen(x, y))
        if len(trail) > 4500:
            trail.pop(0)
        screen.fill(BG)
        for gx in range(0, WIDTH, 50):
            pygame.draw.line(screen, GREY, (gx, 0), (gx, HEIGHT), 1)
        for gy in range(0, HEIGHT, 50):
            pygame.draw.line(screen, GREY, (0, gy), (WIDTH, gy), 1)
        draw_field(screen, manager.field)
        if show_path:
            draw_polyline(screen, manager.path, DARK, 2, closed=manager.closed_path)
        if len(trail) > 2:
            pygame.draw.lines(screen, RED, False, trail, 2)
        draw_car(screen, car)
        if debug:
            draw_debug(screen, car, controller)
        draw_hud(screen, car, controller, manager, paused, show_path, debug)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
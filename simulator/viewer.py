import sys
import os
import pygame
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from simulator.ackermann_model import AckermannCar
from src.control.pure_pursuit import PurePursuit
from src.planning.route_templates import make_lap_route
from src.planning.lap_counter import LapCounter

WIDTH = 900
HEIGHT = 700
SCALE = 180
BG = (245, 245, 245)
BLACK = (20, 20, 20)
BLUE = (50, 90, 220)
RED = (220, 60, 60)
GREEN = (60, 180, 80)
GREY = (190, 190, 190)

def world_to_screen(x, y):
    return int(WIDTH / 2 + x * SCALE), int(HEIGHT / 2 - y * SCALE)

def draw_path(screen, path):
    points = [world_to_screen(x, y) for x, y in path]
    if len(points) > 1:
        pygame.draw.lines(screen, BLACK, False, points, 3)
    for p in points:
        pygame.draw.circle(screen, GREEN, p, 4)

def draw_car(screen, car):
    x, y, theta = car.pose()
    cx, cy = world_to_screen(x, y)
    length = 48
    width = 28
    body = [
        (length / 2, 0),
        (-length / 2, -width / 2),
        (-length / 2, width / 2),
    ]
    points = []
    for px, py in body:
        rx = px * math.cos(theta) - py * math.sin(theta)
        ry = px * math.sin(theta) + py * math.cos(theta)
        points.append((cx + rx, cy - ry))
    pygame.draw.polygon(screen, BLUE, points)
    hx = cx + math.cos(theta) * 45
    hy = cy - math.sin(theta) * 45
    pygame.draw.line(screen, RED, (cx, cy), (hx, hy), 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("WRO FE 2026 Simulator")
    clock = pygame.time.Clock()
    car = AckermannCar()
    car.reset(1.55, 0, math.radians(90))
    path = make_lap_route(3)
    controller = PurePursuit(lookahead=0.5)
    laps = LapCounter(3)
    trail = []
    auto = True
    running = True
    while running:
        dt = clock.tick(50) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    auto = not auto
                if event.key == pygame.K_r:
                    car.reset(1.55, 0, math.radians(90))
                    controller.reset()
                    laps = LapCounter(3)
                    trail = []
        if auto:
            steer, target = controller.update(car.pose(), path)
            car.set_steering(steer)
            if controller.finished(path):
                car.set_speed(0)
            else:
                car.set_speed(0.30)
        else:
            keys = pygame.key.get_pressed()
            speed = 0
            steer = 0
            if keys[pygame.K_w]:
                speed = 0.5
            if keys[pygame.K_s]:
                speed = -0.3
            if keys[pygame.K_a]:
                steer = 25
            if keys[pygame.K_d]:
                steer = -25
            car.set_speed(speed)
            car.set_steering(steer)
        car.update(dt)
        x, y, theta = car.pose()
        lap_count = laps.update(x, y)
        trail.append(world_to_screen(x, y))
        if len(trail) > 2500:
            trail.pop(0)
        screen.fill(BG)
        for gx in range(0, WIDTH, 50):
            pygame.draw.line(screen, GREY, (gx, 0), (gx, HEIGHT), 1)
        for gy in range(0, HEIGHT, 50):
            pygame.draw.line(screen, GREY, (0, gy), (WIDTH, gy), 1)
        draw_path(screen, path)
        if len(trail) > 2:
            pygame.draw.lines(screen, RED, False, trail, 2)
        draw_car(screen, car)
        font = pygame.font.SysFont(None, 28)
        info = font.render(
            f"Auto: {auto} | Laps: {lap_count} | Index: {controller.index} | SPACE auto/manual | R reset",
            True,
            BLACK,
        )
        screen.blit(info, (20, 20))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
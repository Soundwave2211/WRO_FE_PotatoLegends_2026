import pygame
import math
from ackermann_model import AckermannCar


WIDTH = 900
HEIGHT = 700
SCALE = 180  # pixels per metre

BG = (245, 245, 245)
BLACK = (20, 20, 20)
BLUE = (40, 90, 220)
RED = (220, 50, 50)
GREY = (180, 180, 180)


def world_to_screen(x, y):
    screen_x = int(WIDTH / 2 + x * SCALE)
    screen_y = int(HEIGHT / 2 - y * SCALE)
    return screen_x, screen_y


def draw_car(screen, car):
    x, y, theta = car.pose()
    cx, cy = world_to_screen(x, y)

    car_len = 50
    car_wid = 28

    points = [
        (car_len / 2, 0),
        (-car_len / 2, -car_wid / 2),
        (-car_len / 2, car_wid / 2),
    ]

    rotated = []
    for px, py in points:
        rx = px * math.cos(theta) - py * math.sin(theta)
        ry = px * math.sin(theta) + py * math.cos(theta)
        rotated.append((cx + rx, cy - ry))

    pygame.draw.polygon(screen, BLUE, rotated)

    # heading line
    hx = cx + math.cos(theta) * 45
    hy = cy - math.sin(theta) * 45
    pygame.draw.line(screen, RED, (cx, cy), (hx, hy), 3)


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("WRO Ackermann Simulator")

    clock = pygame.time.Clock()
    car = AckermannCar()

    running = True
    speed = 0
    steer = 0

    trail = []

    while running:
        dt = clock.tick(50) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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

        x, y, _ = car.pose()
        trail.append(world_to_screen(x, y))

        if len(trail) > 1000:
            trail.pop(0)

        screen.fill(BG)

        # grid
        for gx in range(0, WIDTH, 50):
            pygame.draw.line(screen, GREY, (gx, 0), (gx, HEIGHT), 1)
        for gy in range(0, HEIGHT, 50):
            pygame.draw.line(screen, GREY, (0, gy), (WIDTH, gy), 1)

        # trail
        if len(trail) > 2:
            pygame.draw.lines(screen, BLACK, False, trail, 2)

        draw_car(screen, car)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
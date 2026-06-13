from dataclasses import dataclass
import math

@dataclass
class RobotState:
    x: float = 0
    y: float = 0
    theta: float = 0
    v: float = 0
    steer: float = 0

class AckermannCar:
    def __init__(self, wheelbase=0.18, max_steer_deg=28, max_speed=1.0):
        self.L = wheelbase
        self.max_steer = math.radians(max_steer_deg)
        self.max_speed = max_speed
        self.state = RobotState()

    def set_speed(self, speed):
        self.state.v = max(-self.max_speed, min(self.max_speed, speed))

    def set_steering(self, angle_deg):
        angle = math.radians(angle_deg)
        self.state.steer = max(-self.max_steer, min(self.max_steer, angle))

    def update(self, dt):
        if dt <= 0:
            return
        s = self.state
        s.x += s.v * math.cos(s.theta) * dt
        s.y += s.v * math.sin(s.theta) * dt
        s.theta += (s.v / self.L) * math.tan(s.steer) * dt
        s.theta = math.atan2(math.sin(s.theta), math.cos(s.theta))

    def pose(self):
        return self.state.x, self.state.y, self.state.theta

    def reset(self, x=0, y=0, theta=0):
        self.state.x = x
        self.state.y = y
        self.state.theta = theta
        self.state.v = 0
        self.state.steer = 0

if __name__ == "__main__":
    car = AckermannCar()
    car.set_speed(0.5)
    car.set_steering(15)
    dt = 0.02

    for i in range(500):
        car.update(dt)
        if i % 50 == 0:
            x, y, theta = car.pose()
            print(round(x, 3), round(y, 3), round(math.degrees(theta), 2))
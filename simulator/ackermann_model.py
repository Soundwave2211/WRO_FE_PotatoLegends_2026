from dataclasses import dataclass
import math

@dataclass
class RobotState:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0
    v: float = 0.0
    steer: float = 0.0

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

    def speed(self):
        return self.state.v

    def steering_deg(self):
        return math.degrees(self.state.steer)

    def reset(self, x=0.0, y=0.0, theta=0.0):
        self.state = RobotState(x=x, y=y, theta=theta)
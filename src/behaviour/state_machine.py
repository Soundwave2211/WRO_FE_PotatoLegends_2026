from simulator.field_generator import WROField
from src.planning.route_templates import open_route, obstacle_route, parking_path
from src.planning.waypoint_generator import heading_at
from src.planning.lap_counter import LapCounter

class ChallengeManager:
    def __init__(self):
        self.mode = "open"
        self.seed = 1
        self.field = None
        self.path = None
        self.closed_path = True
        self.laps = None
        self.state = "FOLLOWING"
        self.load_open()

    def load_open(self, new_seed=False):
        if new_seed:
            self.seed += 1

        self.mode = "open"
        self.field = WROField(seed=self.seed)
        self.path = open_route(self.field)
        self.closed_path = True
        self.laps = LapCounter(len(self.path), laps_required=3)
        self.state = "FOLLOWING"

    def load_obstacle(self, new_seed=False):
        if new_seed:
            self.seed += 1

        self.mode = "obstacle"
        self.field = WROField(seed=self.seed)
        self.path = obstacle_route(self.field)
        self.closed_path = True
        self.laps = LapCounter(len(self.path), laps_required=3)
        self.state = "FOLLOWING"

    def reset_same_mode(self, new_seed=False):
        if self.mode == "open":
            self.load_open(new_seed)
        else:
            self.load_obstacle(new_seed)

    def start_pose(self):
        x, y = self.path[0]
        theta = heading_at(self.path, 0)
        return x, y, theta

    def update_state(self, index, pose):
        if self.state in ["STOPPED", "PARKED", "COLLISION"]:
            return self.state
        if self.closed_path:
            self.laps.update(index)
        if self.mode == "open" and self.laps.done():
            self.state = "STOPPED"
        elif self.mode == "obstacle" and self.laps.done() and self.state == "FOLLOWING":
            self.state = "PARKING"
            self.path = parking_path(self.field, pose)
            self.closed_path = False
        elif self.mode == "obstacle" and self.state == "PARKING":
            if index >= len(self.path) - 3:
                self.state = "PARKED"
        return self.state

    def should_stop(self):
        return self.state in ["STOPPED", "PARKED", "COLLISION"]
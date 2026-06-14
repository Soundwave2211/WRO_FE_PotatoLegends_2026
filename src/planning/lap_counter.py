class LapCounter:
    def __init__(self, laps_required=3):
        self.laps_required = laps_required
        self.laps = 0
        self.was_near_start = False

    def update(self, x, y):
        near_start = abs(x + 1.6) < 0.25 and abs(y + 1.0) < 0.25

        if near_start and not self.was_near_start:
            self.laps += 1

        self.was_near_start = near_start
        return self.laps

    def done(self):
        return self.laps > self.laps_required
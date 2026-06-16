class LapCounter:
    def __init__(self, path_len, laps_required=3):
        self.path_len = max(1, path_len)
        self.laps_required = laps_required
        self.laps = 0
        self.last_index = 0
        self.progress = 0

    def reset(self):
        self.laps = 0
        self.last_index = 0
        self.progress = 0

    def update(self, index):
        diff = index - self.last_index
        if diff < -self.path_len * 0.5:
            diff += self.path_len
        if diff > 0:
            self.progress += diff
        self.last_index = index
        self.laps = int(self.progress / self.path_len)
        return self.laps

    def done(self):
        return self.laps >= self.laps_required
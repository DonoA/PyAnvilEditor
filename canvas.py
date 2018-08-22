import sys, math

class Canvas:
    def __init__(self, world):
        self.world = world

    def brush(self, state):
        self.state = state
        return self

    def square(self, center, side_len):
        strt = math.floor(side_len/2.0)
        end = math.ceil(side_len/2.0)
        for x in range(-strt, end):
            for z in range(-strt, end):
                self.world.get_block((center[0] + x, center[1], center[2] + z)).set_state(self.state)

    def disk(self, center, radius):
        ss = radius+1
        for x in range(-ss, ss):
            for z in range(-ss, ss):
                loc = (center[0] + x, center[1], center[2] + z)
                if Canvas._dist(loc, center) <= (radius + 0.5):
                    self.world.get_block((center[0] + x, center[1], center[2] + z)).set_state(self.state)

    def _dist(loc1, loc2):
        dx = abs(loc1[0] - loc2[0]) ** 2
        dy = abs(loc1[1] - loc2[1]) ** 2
        dz = abs(loc1[2] - loc2[2]) ** 2

        return math.sqrt(dx + dy + dz)
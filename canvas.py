import sys, math

class WorldTask:
    def __init__(self, location, new_state):
        self.location = location
        self.new_state = new_state

class Canvas:
    def __init__(self, world, auto_commit=True):
        self.world = world
        self.work_queue = []
        self.auto_commit = auto_commit

    def brush(self, state):
        self.state = state.clone()
        return self

    def commit(self):
        region_work = {}
        for task in self.work_queue:
            chunk_cords = self.world._get_chunk(task.location)
            region_cords = self.world._get_region_file(chunk_cords)
            if region_cords not in region_work:
                region_work[region_cords] = []
            region_work[region_cords].append(task)

        for chunk, work in region_work.items():
            for task in work:
                self.world.get_block(task.location).set_state(task.new_state)
            self.world.flush()

    def square(self, center, side_len):
        strt = math.floor(side_len/2.0)
        end = math.ceil(side_len/2.0)
        for x in range(-strt, end):
            for z in range(-strt, end):
                loc = (center[0] + x, center[1], center[2] + z)
                self.work_queue.append(WorldTask(loc, self.state))
        if self.auto_commit:
            self.commit()

    def disk(self, center, radius):
        ss = radius+1
        for x in range(-ss, ss):
            for z in range(-ss, ss):
                loc = (center[0] + x, center[1], center[2] + z)
                if Canvas._dist(loc, center) <= (radius + 0.5):
                    self.world.get_block((center[0] + x, center[1], center[2] + z)).set_state(self.state)
        if self.auto_commit:
            self.commit()

    def _dist(loc1, loc2):
        dx = abs(loc1[0] - loc2[0]) ** 2
        dy = abs(loc1[1] - loc2[1]) ** 2
        dz = abs(loc1[2] - loc2[2]) ** 2

        return math.sqrt(dx + dy + dz)
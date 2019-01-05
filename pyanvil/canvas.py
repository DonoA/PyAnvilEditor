import sys, math
from pyanvil.schematic import Schematic

class WorldTask:
    def __init__(self, location, new_state):
        self.location = location
        self.new_state = new_state

class Canvas:

    def __init__(self, world, auto_commit=True):
        self.world = world
        self.work_queue = []
        self.auto_commit = auto_commit
        self.selection = set()

    def fill(self, state):
        my_state = state.clone()
        for b in list(self.selection):
            self.work_queue.append(WorldTask(b, my_state))

        self.selection.clear()
        
        if self.auto_commit:
            self.commit()

    def deselect(self):
        self.selection.clear()

    def copy(self):
        min_x = min([l[0] for l in self.selection])
        min_y = min([l[1] for l in self.selection])
        min_z = min([l[2] for l in self.selection])
        print(min_x, min_y, min_z)
        new_schem = Schematic({
            (loc[0] - min_x, loc[1] - min_y, loc[2] - min_z): self.world.get_block(loc).get_state() for loc in self.selection
        })
        self.selection.clear()
        return new_schem

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

    def select_rectangle(self, p1, p2):
        self._rect(p1, p2, True)
        return self

    def deselect_rectangle(self, p1, p2):
        self._rect(p1, p2, False)
        return self

    def _rect(self, p1, p2, select):
        for x in range(p1[0], p2[0] + 1):
            for y in range(p1[1], p2[1] + 1):
                for z in range(p1[2], p2[2] + 1):
                    loc = (x, y, z)
                    if select:
                        self.selection.add(loc)
                    else:
                        self.selection.remove(loc)

    # def select_oval(self, p1, p2):
    #     self._oval(center, radius, True)
    #     return self

    # def deselect_oval(self, p1, p2):
    #     self._oval(center, radius, False)
    #     return self

    # def _oval(self, p1, p2, select):
    #     ss = radius+1
    #     for x in range(-ss, ss):
    #         for z in range(-ss, ss):
    #             loc = (center[0] + x, center[1], center[2] + z)
    #             if Canvas._dist(loc, center) <= (radius + 0.5):
    #                 if select:
    #                     self.selection.add(loc)
    #                 else:
    #                     self.selection.remove(loc)

    def _dist(loc1, loc2):
        dx = abs(loc1[0] - loc2[0]) ** 2
        dy = abs(loc1[1] - loc2[1]) ** 2
        dz = abs(loc1[2] - loc2[2]) ** 2

        return math.sqrt(dx + dy + dz)
class Schematic:

    def __init__(self, state_map):
        self.state_map = state_map

    def paste(self, world, corner):
        for loc, state in self.state_map.items():
            shift_loc = (loc[0] + corner[0], loc[1] + corner[1], loc[2] + corner[2])
            world.get_block(shift_loc).set_state(state)
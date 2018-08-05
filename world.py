import sys

class Block:
    def __init__(self, name, props):
        self.name = name
        self.props = props

class Chunk:

    def __init__(self, blocks):
        self.blocks = {}
        for section in blocks:
            self.blocks[section] = [[[0 for z in range(16)] for y in range(16)] for x in range(16)]
            for y in range(16):
                for z in range(16):
                    for x in range(16):
                        self.blocks[section][x][y][z] = blocks[section][x + z * 16 + y * 16 ** 2]
        
    
    # Blockstates are packed based on the number of values in the pallet. 
    # This selects the pack size, then splits out the ids
    def unpack(raw_nbt):
        blocks = {}
        for section in [raw_nbt.get("Level").get("Sections").children[3]]:
            flatstates = [c.get() for c in section.get("BlockStates").children]
            pack_size = int((len(flatstates) * 64) / (16**3))
            states = [
                Chunk._read_width_from_loc(flatstates, pack_size, i) for i in range(16**3)
            ]
            print(pack_size)
            states = [
                section.get("Palette").children[i] for i in states
            ]
            blocks[section.get("Y").get()] = [
                Block(state.get("Name").get(), state.get("Properties").toDict() if state.has("Properties") else {}) for state in states
            ]

        return blocks

    def _read_width_from_loc(long_list, width, possition):
        offset = possition * width
        # refrence the space we want to select from to make things a little easier
        search_space = long_list[int(offset/64)]
        spc = 64
        if int(offset/64) != int((offset + width)/64) and int((offset + width)/64) < len(long_list):
            # love ya python!
            search_space = (search_space << 64) + long_list[int((offset + width)/64)]
            spc = 128

        # create a mask of size 'width' of 1 bits
        mask = (2 ** width) - 1
        # shift it out to where we need for the mask
        mask = mask << (offset % 64)
        # select the bits we need
        comp = search_space & mask
        # move them back to where they should be
        comp = comp >> (offset % 64)

        print(format(search_space, '#0' + str(spc) + 'b'))
        print(format(mask, '#0' + str(spc) + 'b'))

        return comp
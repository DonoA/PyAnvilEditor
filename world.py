import sys, math, nbt, gzip, zlib, stream

class Block:
    def __init__(self, name, props):
        self.name = name
        self.props = props

class Chunk:

    def __init__(self, xpos, zpos, blocks):
        self.xpos = xpos
        self.zpos = zpos

        self.blocks = blocks
        
    def get(self, block_pos):
        x = block_pos[0]
        y = block_pos[1]
        z = block_pos[2] - 1
        print(x%16, y%16, z%16)
        # print([s.name for s in self.blocks[int(y/16)]])
        for x1 in range(16):
            for y1 in range(16):
                for z1 in range(16):
                    if "water" in self.blocks[int(y/16)][(x1 % 16) + (z1 % 16) * 16 + (y1 % 16) * 16 ** 2].name:
                        print(x1, y1, z1, self.blocks[int(y/16)][(x1 % 16) + (z1 % 16) * 16 + (y1 % 16) * 16 ** 2].name)
        return self.blocks[int(y/16)][(x % 16) + (z % 16) * 16 + (y % 16) * 16 ** 2]

    # Blockstates are packed based on the number of values in the pallet. 
    # This selects the pack size, then splits out the ids
    def unpack(raw_nbt):
        blocks = {}
        for section in raw_nbt.get("Level").get("Sections").children:
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
                Block(state.get("Name").get(), state.get("Properties").to_dict() if state.has("Properties") else {}) for state in states
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
        comp = comp >> ((offset % 64) + (1 if spc == 128 and width % 2 != 0 else 0))

        # print(comp)
        # print(format(long_list[int(offset/64)], '#064b'))
        # print(format(long_list[int(offset/64) + 1], '#064b'))
        # print(format(search_space, '#0' + str(spc) + 'b'))
        # print(format(mask, '#0' + str(spc) + 'b'))
        # print(bin(comp))

        # sys.exit(0)

        return comp

class World:
    def __init__(self, file_name):
        self.file_name = file_name
        self.chunks = {}
    
    def get_block(self, block_pos):
        chunk_pos = self._get_chunk(block_pos)
        if chunk_pos not in self.chunks:
            self._load_chunk(chunk_pos)
        
        chunk = self.chunks[chunk_pos]
        return chunk.get(block_pos)
        
    def _load_chunk(self, chunk_pos):
        with open(self.file_name + "/region/" + self._get_region_file(chunk_pos), mode="rb") as region:
            locations = list(filter(
                lambda x: x[0] > 0,
                [
                    [
                        int.from_bytes(region.read(3), byteorder='big', signed=False) * 4096, 
                        int.from_bytes(region.read(1), byteorder='big', signed=False) * 4096
                    ] for i in range(1024)
                ]
            ))

            timestamps = region.read(4096)

            for l in locations:
                c_loc = self._get_binary_location_at(region, l[0])
                if c_loc == chunk_pos:
                    # chunk = self._load_binary_chunk_at(region, locations[((chunk_pos[0] % 32) + (chunk_pos[1] % 32) * 32)][0])
                    print("Found!")
                    chunk = self._load_binary_chunk_at(region, l[0])
                    self.chunks[chunk_pos] = chunk
                    break

    def _get_binary_location_at(self, region_file, offset):
        region_file.seek(offset)
        datalen = int.from_bytes(region_file.read(4), byteorder='big', signed=False)
        compr = region_file.read(1)
        decompressed = zlib.decompress(region_file.read(datalen))
        data = nbt.parse_nbt(stream.Stream(decompressed))

        return (data.get("Level").get("xPos").get(), data.get("Level").get("zPos").get())

    def _load_binary_chunk_at(self, region_file, offset):
        region_file.seek(offset)
        datalen = int.from_bytes(region_file.read(4), byteorder='big', signed=False)
        compr = region_file.read(1)
        decompressed = zlib.decompress(region_file.read(datalen))
        data = nbt.parse_nbt(stream.Stream(decompressed))
        # data.print()
        chunk_pos = (data.get("Level").get("xPos").get(), data.get("Level").get("zPos").get())
        chunk = Chunk(
            chunk_pos[0],
            chunk_pos[1],
            Chunk.unpack(data)
        )
        return chunk

    def _get_region_file(self, chunk_pos):
        return "r." + '.'.join([str(x) for x in self._get_region(chunk_pos)]) + '.mca'


    def _get_chunk(self, block_pos):
        return (math.floor(block_pos[0] / 16), math.floor(block_pos[2] / 16))

    def _get_region(self, chunk_pos):
        return (math.floor(chunk_pos[0] / 32), math.floor(chunk_pos[1] / 32))
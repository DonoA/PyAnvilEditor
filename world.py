import sys, math, nbt, gzip, zlib, stream

class BlockState:
    def __init__(self, name, props):
        self.name = name
        self.props = props

    def __str__(self):
        return "BlockState(" + self.name + "," + str(self.props) + ")"

class Block:
    def __init__(self, state):
        self.state = state

    def __str__(self):
        return "Block(" + str(self.state) + ")"

    def set_state(self, state):
        self.state = state

class ChunkSection:
    def __init__(self, blocks, palette):
        self.blocks = blocks
        self.palette = palette

    def get_block(self, block_pos):
        x = block_pos[0]
        y = block_pos[1]
        z = block_pos[2]

        return self.blocks[x + z * 16 + y * 16 ** 2]

class Chunk:
    def __init__(self, xpos, zpos, sections):
        self.xpos = xpos
        self.zpos = zpos
        self.sections = sections
        
    def get_block(self, block_pos):
        return self.get_section(block_pos[1]).get_block([n % 16 for n in block_pos])

    def get_section(self, y):
        return self.sections[int(y/16)]

    def find_like(self, string):
        results = []
        for sec in self.sections:
            section = self.sections[sec]
            for x1 in range(16):
                for y1 in range(16):
                    for z1 in range(16):
                        if string in section.get_block((x1, y1, z1)).state.name:
                            results.append((
                                (x1 + self.xpos * 16, y1 + sec * 16, z1 + self.zpos * 16), 
                                section.get_block((x1, y1, z1))
                            ))
        return results

    # Blockstates are packed based on the number of values in the pallet. 
    # This selects the pack size, then splits out the ids
    def unpack(raw_nbt):
        sections = {}
        for section in raw_nbt.get("Level").get("Sections").children:
            flatstates = [c.get() for c in section.get("BlockStates").children]
            pack_size = int((len(flatstates) * 64) / (16**3))
            states = [
                Chunk._read_width_from_loc(flatstates, pack_size, i) for i in range(16**3)
            ]
            palette = [ 
                BlockState(
                    section.get("Palette").children[i].get("Name").get(),
                    section.get("Palette").children[i].get("Properties").to_dict() if section.get("Palette").children[i].has("Properties") else {}
                ) for i in range(len(section.get("Palette").children))
            ]
            blocks = [
                Block(palette[state]) for state in states
            ]
            sections[section.get("Y").get()] = ChunkSection(blocks, palette)

        return sections

    def pack(self):
        pass

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
        comp = comp >> ((offset % 64) + ((width - 4) if spc == 128 else 0))

        return comp

class World:
    def __init__(self, file_name, save_location=""):
        self.file_name = file_name
        self.save_location = save_location
        self.chunks = {}

    def __enter__(self):
        return self
    
    def __exit__(self, typ, val, trace):
        self.close()

    def close(self):
        for c in self.chunks:
            pass

    def get_block(self, block_pos):
        chunk_pos = self._get_chunk(block_pos)
        chunk = self.get_chunk(chunk_pos)
        return chunk.get_block(block_pos)

    def get_chunk(self, chunk_pos):
        if chunk_pos not in self.chunks:
            self._load_chunk(chunk_pos)

        return self.chunks[chunk_pos]

    def _load_chunk(self, chunk_pos):
        with open(self.save_location + "/" + self.file_name + "/region/" + self._get_region_file(chunk_pos), mode="rb") as region:
            locations = [[
                        int.from_bytes(region.read(3), byteorder='big', signed=False) * 4096, 
                        int.from_bytes(region.read(1), byteorder='big', signed=False) * 4096
                    ] for i in range(1024) ]

            timestamps = region.read(4096)

            chunk = self._load_binary_chunk_at(region, locations[((chunk_pos[0] % 32) + (chunk_pos[1] % 32) * 32)][0])
            self.chunks[chunk_pos] = chunk

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
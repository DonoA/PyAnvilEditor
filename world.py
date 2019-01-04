import sys, math, nbt, gzip, zlib, stream, time, os
from biomes import Biome

class BlockState:
    def __init__(self, name, props):
        self.name = name
        self.props = props
        self.id = None

    def __str__(self):
        return 'BlockState(' + self.name + ',' + str(self.props) + ')'

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name and self.props == other.props

    def clone(self):
        return BlockState(self.name, self.props.copy())

class Block:
    def __init__(self, state, block_light, sky_light):
        self._state = state
        self.block_light = 0
        self.sky_light = 0
        self._dirty = True

    def __str__(self):
        return f'Block({str(self._state)}, {self.block_light}, {self.sky_light})'

    def set_state(self, state):
        self._dirty = True
        self._state = state

    def get_state(self):
        return self._state.clone()

class ChunkSection:
    def __init__(self, blocks, raw_section, y_index):
        self.blocks = blocks
        self.raw_section = raw_section
        self.y_index = y_index

    def get_block(self, block_pos):
        x = block_pos[0]
        y = block_pos[1]
        z = block_pos[2]

        return self.blocks[x + z * 16 + y * 16 ** 2]

    def serialize(self):
        serial_section = self.raw_section
        dirty = any([b._dirty for b in self.blocks])
        if dirty:
            self.palette = list(set([ b._state for b in self.blocks ] + [ BlockState('minecraft:air', {}) ]))
            self.palette.sort(key=lambda s: s.name)
            serial_section.add_child(nbt.ByteTag('Y', self.y_index))
            mat_id_mapping = {self.palette[i]: i for i in range(len(self.palette))}
            new_palette = self._serialize_palette()
            serial_section.add_child(new_palette)
            serial_section.add_child(self._serialize_blockstates(mat_id_mapping))
        
        if not serial_section.has('SkyLight'):
            serial_section.add_child(nbt.ByteArrayTag('SkyLight', [nbt.ByteTag('None', -1) for i in range(2048)]))

        if not serial_section.has('BlockLight'):
            serial_section.add_child(nbt.ByteArrayTag('BlockLight', [nbt.ByteTag('None', -1) for i in range(2048)]))

        return serial_section

    def _serialize_palette(self):
        serial_palette = nbt.ListTag('Palette', nbt.CompoundTag.clazz_id)
        for state in self.palette:
            palette_item = nbt.CompoundTag('None', children=[
                nbt.StringTag('Name', state.name)
            ])
            if len(state.props) != 0:
                serial_props = nbt.CompoundTag('Properties')
                for name, val in state.props.items():
                    serial_props.add_child(nbt.StringTag(name, str(val)))
                palette_item.add_child(serial_props)
            serial_palette.add_child(palette_item)
        
        return serial_palette

    def _serialize_blockstates(self, state_mapping):
        serial_states = nbt.LongArrayTag('BlockStates')
        width = math.ceil(math.log(len(self.palette), 2))
        if width < 4:
            width = 4
        data = 0
        for block in reversed(self.blocks):
            data = (data << width) + state_mapping[block._state]

        mask = (2 ** 64) - 1
        for i in range(int((len(self.blocks) * width)/64)):
            lng = data & mask
            lng = int.from_bytes(lng.to_bytes(8, byteorder='big', signed=False), byteorder='big', signed=True)
            serial_states.add_child(nbt.LongTag('', lng))
            data = data >> 64
        return serial_states

class Chunk:

    def __init__(self, xpos, zpos, sections, raw_nbt, orig_size):
        self.xpos = xpos
        self.zpos = zpos
        self.sections = sections
        self.raw_nbt = raw_nbt
        self.biomes = [Biome.biome_list[i] for i in self.raw_nbt.get('Level').get('Biomes').get()]
        self.orig_size = orig_size
        
    def get_block(self, block_pos):
        return self.get_section(block_pos[1]).get_block([n % 16 for n in block_pos])

    def get_section(self, y):
        key = int(y/16)
        if key not in self.sections:
            self.sections[key] = ChunkSection(
                [Block(BlockState('minecraft:air', {}), 0, 0) for i in range(4096)],
                nbt.CompoundTag('None'),
                key
            )
        return self.sections[key]

    def find_like(self, string):
        results = []
        for sec in self.sections:
            section = self.sections[sec]
            for x1 in range(16):
                for y1 in range(16):
                    for z1 in range(16):
                        if string in section.get_block((x1, y1, z1))._state.name:
                            results.append((
                                (x1 + self.xpos * 16, y1 + sec * 16, z1 + self.zpos * 16), 
                                section.get_block((x1, y1, z1))
                            ))
        return results

    # Blockstates are packed based on the number of values in the pallet. 
    # This selects the pack size, then splits out the ids
    def unpack(raw_nbt):
        sections = {}
        for section in raw_nbt.get('Level').get('Sections').children:
            flatstates = [c.get() for c in section.get('BlockStates').children]
            pack_size = int((len(flatstates) * 64) / (16**3))
            states = [
                Chunk._read_width_from_loc(flatstates, pack_size, i) for i in range(16**3)
            ]
            palette = [ 
                BlockState(
                    state.get('Name').get(),
                    state.get('Properties').to_dict() if state.has('Properties') else {}
                ) for state in section.get('Palette').children
            ]
            block_lights = Chunk._divide_nibbles(section.get('BlockLight').get())
            sky_lights = Chunk._divide_nibbles(section.get('SkyLight').get())
            blocks = [
                Block(palette[states[i]], block_lights[i], sky_lights[i]) for i in range(len(states))
            ]
            sections[section.get('Y').get()] = ChunkSection(blocks, section, section.get('Y').get())

        return sections

    def _divide_nibbles(arry):
        rtn = []
        f2_mask = 2**4-1
        f1_mask = f2_mask << 4
        for s in arry:
            rtn.append(s & f1_mask)
            rtn.append(s & f2_mask)

        return rtn

    def pack(self):
        new_sections = nbt.ListTag('Sections', nbt.CompoundTag.clazz_id, children=[
            self.sections[sec].serialize() for sec in self.sections
        ])
        new_nbt = self.raw_nbt.clone()
        new_nbt.get('Level').add_child(new_sections)

        return new_nbt

    def _read_width_from_loc(long_list, width, possition):
        offset = possition * width
        # if this is split across two nums
        if (offset % 64) + width > 64:
            # Find the lengths on each side of the split
            side1len = 64 - ((offset) % 64)
            side2len = ((offset + width) % 64)
            # Select the sections we want from each
            side1 = Chunk._read_bits(long_list[int(offset/64)], side1len, offset % 64)
            side2 = Chunk._read_bits(long_list[int((offset + width)/64)], side2len, 0)
            # Join them
            comp = (side2 << side1len) + side1
            return comp
        else:
            comp = Chunk._read_bits(long_list[int(offset/64)], width, offset % 64)
            return comp

    def _read_bits(num, width, start):
        # create a mask of size 'width' of 1 bits
        mask = (2 ** width) - 1
        # shift it out to where we need for the mask
        mask = mask << start
        # select the bits we need
        comp = num & mask
        # move them back to where they should be
        comp = comp >> start

        return comp

    def __str__(self):
        return "Chunk(" + str(self.xpos) + "," + str(self.zpos) + ")"

class World:
    def __init__(self, file_name, save_location=''):
        self.file_name = file_name
        self.save_location = save_location
        if not os.path.exists(save_location):
            raise FileNotFoundError('No such folder ' + save_location)
        if not os.path.exists(save_location + '/' + file_name):
            raise FileNotFoundError('No such save ' + save_location)
        self.chunks = {}

    def __enter__(self):
        return self
    
    def __exit__(self, typ, val, trace):
        if typ is None:
            self.close()

    def close(self):
        chunks_by_region = {}
        for chunk_pos, chunk in self.chunks.items():
            region = self._get_region_file(chunk_pos)
            if region not in chunks_by_region:
                chunks_by_region[region] = []
            chunks_by_region[region].append(chunk)

        for region_name, chunks in chunks_by_region.items():
            with open(self.save_location + '/' + self.file_name + '/region/' + region_name, mode='r+b') as region:
                region.seek(0)
                locations = [[
                            int.from_bytes(region.read(3), byteorder='big', signed=False) * 4096, 
                            int.from_bytes(region.read(1), byteorder='big', signed=False) * 4096
                        ] for i in range(1024) ]

                timestamps = [int.from_bytes(region.read(4), byteorder='big', signed=False) for i in range(1024)]

                data_in_file = bytearray(region.read())

                chunks.sort(key=lambda chunk: locations[((chunk.xpos % 32) + (chunk.zpos % 32) * 32)][0])
                # print("writing chunks", [str(c) + ":" + str(locations[((chunk.xpos % 32) + (chunk.zpos % 32) * 32)][0]) for c in chunks])

                for chunk in chunks:
                    strm = stream.OutputStream()
                    chunkNBT = chunk.pack()
                    chunkNBT.serialize(strm)
                    data = zlib.compress(strm.get_data())
                    datalen = len(data)
                    block_data_len = math.ceil((datalen + 5)/4096.0)*4096
                    data = (datalen + 1).to_bytes(4, byteorder='big', signed=False) + \
                        (2).to_bytes(1, byteorder='big', signed=False) + \
                        data + \
                        (0).to_bytes(block_data_len - (datalen + 5), byteorder='big', signed=False)

                    # timestamps[((chunk.xpos % 32) + (chunk.zpos % 32) * 32)] = int(time.time())

                    loc = locations[((chunk.xpos % 32) + (chunk.zpos % 32) * 32)]
                    data_len_diff = block_data_len - loc[1]
                    if data_len_diff != 0:
                        # chunkNBT.print()
                        # print('===vs===')
                        # chunk.raw_nbt.print()
                        print('Danger: Diff is not 0, shifting required!')
                        sys.exit(0)

                    locations[((chunk.xpos % 32) + (chunk.zpos % 32) * 32)][1] = block_data_len

                    if loc[0] == 0 or loc[1] == 0:
                        print("Chunk not generated", chunk)
                        sys.exit(0)

                    for c_loc in locations:
                        if c_loc[0] > loc[0]:
                            c_loc[0] = c_loc[0] + data_len_diff

                    data_in_file[(loc[0] - 8192):(loc[0] + loc[1] - 8192)] = data
                    print('Saving', chunk, 'With', {'loc': loc, 'new_len': datalen, 'old_len': chunk.orig_size, 'sector_len': block_data_len})

                region.seek(0)

                for c_loc in locations:
                    region.write(int(c_loc[0]/4096).to_bytes(3, byteorder='big', signed=False))
                    region.write(int(c_loc[1]/4096).to_bytes(1, byteorder='big', signed=False))

                for ts in timestamps:
                    region.write(ts.to_bytes(4, byteorder='big', signed=False))

                region.write(data_in_file)

                required_padding = (math.ceil(region.tell()/4096.0) * 4096) - region.tell()

                region.write((0).to_bytes(required_padding, byteorder='big', signed=False))

    def get_block(self, block_pos):
        chunk_pos = self._get_chunk(block_pos)
        chunk = self.get_chunk(chunk_pos)
        return chunk.get_block(block_pos)

    def get_chunk(self, chunk_pos):
        if chunk_pos not in self.chunks:
            self._load_chunk(chunk_pos)

        return self.chunks[chunk_pos]

    def _load_chunk(self, chunk_pos):
        with open(self.save_location + '/' + self.file_name + '/region/' + self._get_region_file(chunk_pos), mode='rb') as region:
            locations = [[
                        int.from_bytes(region.read(3), byteorder='big', signed=False) * 4096, 
                        int.from_bytes(region.read(1), byteorder='big', signed=False) * 4096
                    ] for i in range(1024) ]

            timestamps = region.read(4096)

            loc = locations[((chunk_pos[0] % 32) + (chunk_pos[1] % 32) * 32)]
            # print(loc)

            print('Loading', chunk_pos,'from', region.name)
            chunk = self._load_binary_chunk_at(region, loc[0], loc[1])
            self.chunks[chunk_pos] = chunk

    def _load_binary_chunk_at(self, region_file, offset, max_size):
        region_file.seek(offset)
        datalen = int.from_bytes(region_file.read(4), byteorder='big', signed=False)
        # print('Len', datalen, 'Max', max_size)
        compr = region_file.read(1)
        # print('Compr', compr)
        # print(region_file.tell()-5, datalen)
        decompressed = zlib.decompress(region_file.read(datalen-1))
        data = nbt.parse_nbt(stream.InputStream(decompressed))
        chunk_pos = (data.get('Level').get('xPos').get(), data.get('Level').get('zPos').get())
        chunk = Chunk(
            chunk_pos[0],
            chunk_pos[1],
            Chunk.unpack(data),
            data,
            datalen
        )
        return chunk

    def _get_region_file(self, chunk_pos):
        return 'r.' + '.'.join([str(x) for x in self._get_region(chunk_pos)]) + '.mca'


    def _get_chunk(self, block_pos):
        return (math.floor(block_pos[0] / 16), math.floor(block_pos[2] / 16))

    def _get_region(self, chunk_pos):
        return (math.floor(chunk_pos[0] / 32), math.floor(chunk_pos[1] / 32))
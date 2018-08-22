PyAnvilEditor
===
A python based library for loading and saving minecraft world files. The project includes a method for creating, editing, and saving nbt files as well as a method for loading worlds and editing the chunks and blocks within them.

## NBT
The `nbt` module is designed to load and save uncompressed binary data in nbt format. Calling `parse_nbt` on a stream of binary data will return a `CompoundTag` containing the data in the stream. NBT decoding for Minecraft 1.13 includes the following tags:
- `ByteTag`: 8 bit, signed
- `ShortTag`: 16 bit, signed
- `IntTag`: 32 bit, signed
- `LongTag`: 64 bit, signed
- `FloatTag`: 32 bit, signed
- `DoubleTag`: 64 bit, signed
- `ByteArray`: List of nameless 8 bit signed numbers
- `IntArray`: List of nameless 32 bit signed numbers
- `LongArray`: List of nameless 64 bit signed numbers
- `StringTag`: List of bytes representing UTF-8 chars
- `ListTag`: List any other tag
- `CompundTag`: Unordered list of named tags of any type

Calling `serialize` on an nbt tag with a file stream will write the binary data of the nbt tag to the file. The `stream.Output` class can also be used to emulate a file buffer.

For example, to get the name of a region from the `level.dat` file of a region folder:
```python
import nbt, stream, gzip

# Open the file for reading in binary mode (level.dat is just gzipped)
with gzip.open('level.dat', mode='rb') as level:
    # Read the file in to an input stream
    in_stream = stream.InputStream(level.read())
    # Decode the stream
    level_data = nbt.parse_nbt(in_stream)
    # Get the value of Data > LevelName
    lvl_name = level_data.get("Data").get("LevelName").get()
    # lvl_name is now a string containing the name of the level used

```

## World
The `world` module allows the modification and saving of a whole world file. An example of getting a single block using the world module might look like the following:
```python
import world

# Load the world folder relative to the current working dir
with world.World('myWorld') as myWorld:
    # All locations are stored as tuples
    myBlockPos = (15, 10, 25)
    # Get the block object at the given location
    myBlock = myWorld.get_block(myBlockPos)
    # Set the state of the block to an iron block
    myBlock.set_state(world.BlockState('minecraft:iron_block', {}))

# Once the with closes, the world is saved
```

## Canvas
The `canvas` module allows for easy drawing within a world object. The canvas can draw:
- Squares
- Disks
- Cubes
- Spheres
- Pyramids

To use the canvas, we simply make a new instance an pass in the world we want to use:
```python
import world, canvas

# Load the world folder relative to the current working dir
with world.World('myWorld') as myWorld:
    # create the canvas to draw on
    cvs = canvas.Canvas(myWorld)
    # draw a disk centered at (10, 10, 10) and made of gold ore block
    cvs.brush(world.BlockState('minecraft:gold_ore', {})).disk((10, 10, 10))

# Once the world is closed, the changes have been saved and can be viewed in game
```
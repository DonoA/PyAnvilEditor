PyAnvilEditor
===
A python based library for loading and saving minecraft world files. The project includes a method for creating, editing, and saving nbt files as well as a method for loading worlds and editing the chunks and blocks within them.

## NBT
The `nbt` module can load uncompressed binary data in nbt format. Calling `parse_nbt` on a stream of binary data will return a `CompoundTag` encoding the data in the stream. NBT decoding for Minecraft 1.13 includes the following tags:
- `ByteTag`
- `ShortTag`
- `IntTag`
- `LongTag`
- `FloatTag`
- `DoubleTag`
- `ByteArray`
- `IntArray`
- `LongArray`
- `StringTag`
- `ListTag`
- `CompundTag`

Calling `serialize` on an nbt tag with a file stream will write the binary data of the nbt tag to the file.

## World
The `world` module allows the modification and saving of a whole world file. An example of getting a single block using the world module might look like the following:
```
import world
myWorld = world.World("myWorld")
myBlockPos = (15, 10, 25)
myBlock = myWorld.get_block(myBlockPos)
```

`myBlock` now contains the name and properties of the block state at the given location.

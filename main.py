import sys, world

# WORLD_FOLDER = "newWorld/"

# with gzip.open(WORLD_FOLDER + "level.dat", mode="rb") as level:
#     strm = stream.Stream(level.read())
#     data = nbt.parse_nbt(strm)
#     data.print()

world = world.World("newWorld")
print(world.get_block((68, 32, 54)).name)
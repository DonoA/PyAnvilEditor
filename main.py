import sys, world

world = world.World("New World", save_location="/home/dallen/snap/minecraft/common/.minecraft/saves")
results = world.get_chunk((6, 6)).find_like("gold")
for r in results:
    print(r[0], r[1].state)
print(world.get_block((100, 200, 100)))
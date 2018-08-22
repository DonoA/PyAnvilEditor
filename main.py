import sys, world, canvas

with world.World('SF4', save_location='/home/dallen/snap/minecraft/common/.minecraft/saves') as wrld:
    print('World loaded!')
    cv = canvas.Canvas(wrld)
    for i in range(10, 20, 2):
        cv.brush(world.BlockState('minecraft:gold_block', {})).square((25, i, 25), 10)
        cv.brush(world.BlockState('minecraft:air', {})).disk((25, i, 25), 3)

print('Saved!')
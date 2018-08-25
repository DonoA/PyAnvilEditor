import sys, world, canvas

with world.World('Copy of New World', save_location='/home/dallen/snap/minecraft/common/.minecraft/saves') as wrld:
    print('World loaded!')
    cv = canvas.Canvas(wrld)
    cv.brush(world.BlockState('minecraft:gold_block', {})).square((30, 40, 30), 50)
    # print("=====")
    # cv.brush(world.BlockState('minecraft:air', {})).square((30, 3, 30), 10)
    # cv.brush(world.BlockState('minecraft:gold_block', {})).square((35, 4, 35), 10)

print('Saved!')
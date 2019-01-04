#!/bin/python3
import sys, world, canvas

with world.World('A', save_location='/home/dallen/.minecraft/saves') as wrld:
    print('World loaded!')
    # blk = wrld.get_block((8, 73, 150))
    # print(blk)
    cv = canvas.Canvas(wrld)
    cv.brush(world.BlockState('minecraft:gold_block', {})).square((106, 95, -252), 100)

print('Saved!')
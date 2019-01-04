#!/bin/python3
import sys
from world import World, BlockState
from canvas import Canvas
from materials import Material
from biomes import Biome

with World('A', save_location='/home/dallen/.minecraft/saves') as wrld:
    print('World loaded!')
    blk = wrld.get_block((106, 95, -252))#(8, 73, 150))
    print(blk)
    cv = Canvas(wrld)
    cv.brush(BlockState(Material.gold_block, {})).square((106, 95, -252), 100)

print('Saved!')
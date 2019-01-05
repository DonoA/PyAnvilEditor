#!/bin/python3
import sys
from world import World, BlockState
from canvas import Canvas
from materials import Material
from biomes import Biome

with World('A', save_location='/home/dallen/.minecraft/saves', debug=True) as wrld:
    print('World loaded!')
    cv = wrld.get_canvas()
    cv.brush(BlockState(Material.diamond_block, {})).square((106, 90, -252), 100)

print('Saved!')
#!/bin/python3
import sys
from world import World, BlockState
from canvas import Canvas
from materials import Material
from biomes import Biome

with World('A', save_location='/home/dallen/.minecraft/saves', debug=True) as wrld:
    print('World loaded!')
    cv = wrld.get_canvas()
    cv.select_rectangle((50, 90, -260), (60, 92, -220)).fill(BlockState(Material.diamond_block, {}))
    cv.select_rectangle((156, 96, -271), (177, 131, -249)).copy().paste(wrld, (100, 110, -250))

print('Saved!')
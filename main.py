#!/bin/python3
import sys
from pyanvil import World, BlockState, Material

with World('A', save_location='/home/dallen/.minecraft/saves', debug=True) as wrld:
    cv = wrld.get_canvas()
    cv.select_rectangle((334, 67, -240), (347, 100, -222)).copy().paste(wrld, (411, 105, -302))
    cv.select_rectangle((334, 67, -240), (347, 100, -222)).fill(BlockState(Material.diamond_block, {}))

print('Saved!')
#!/bin/python3
import sys
from world import World, BlockState
from canvas import Canvas
from materials import Material
from biomes import Biome

with World('A', save_location='/home/dallen/.minecraft/saves') as wrld:
    print('World loaded!')
    wrld.get_block((99, 95, -203)).set_state(Material.diamond_block)
    wrld.get_block((99, 94, -203)).set_state(Material.coal_block)
    wrld.get_block((99, 93, -203)).set_state(Material.gold_block)
    wrld.get_block((99, 92, -203)).set_state(Material.iron_block)
    wrld.get_block((99, 91, -203)).set_state(Material.glowstone)

    wrld.get_block((98, 95, -203)).set_state(Material.diamond_ore)
    wrld.get_block((98, 94, -203)).set_state(Material.coal_ore)
    wrld.get_block((98, 93, -203)).set_state(Material.gold_ore)
    wrld.get_block((98, 92, -203)).set_state(Material.iron_ore)
    wrld.get_block((98, 91, -203)).set_state(Material.nether_bricks)

    wrld.get_block((100, 95, -203)).set_state(Material.acacia_planks)
    wrld.get_block((100, 94, -203)).set_state(Material.birch_planks)
    wrld.get_block((100, 93, -203)).set_state(Material.dark_oak_planks)
    wrld.get_block((100, 92, -203)).set_state(Material.jungle_planks)
    wrld.get_block((100, 91, -203)).set_state(Material.spruce_planks)

    wrld.get_block((101, 95, -203)).set_state(Material.stone)
    wrld.get_block((101, 94, -203)).set_state(Material.andesite)
    wrld.get_block((101, 93, -203)).set_state(Material.gravel)
    wrld.get_block((101, 92, -203)).set_state(Material.gray_wool)
    wrld.get_block((101, 91, -203)).set_state(Material.black_wool)
    
    # print(blk)
    # cv = Canvas(wrld)
    # cv.brush(BlockState(Material.gold_block, {})).square((106, 95, -252), 100)

print('Saved!')
import sys, world

with world.World('New World', save_location='/home/dallen/snap/minecraft/common/.minecraft/saves') as wrld:
    print('World loaded!')
    # results = world.get_chunk((6, 6)).find_like('redstone_wall_torch')
    # for r in results:
    #     print(r[0], r[1])
    #     print((r[0][0] % 16) + (r[0][2] % 16) * 16 + (r[0][1] % 16) * 16 ** 2)
    ns = world.BlockState('minecraft:air', {})
    chnk = wrld.get_chunk((6, 4))
    for s in chnk.sections:
        sec = chnk.sections[s]
        for b in sec.blocks:
            b.set_state(ns)

print('Saved!')
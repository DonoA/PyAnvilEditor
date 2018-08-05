import nbt, gzip, zlib, stream, sys

WORLD_FOLDER = "world/"

# with gzip.open(WORLD_FOLDER + "playerdata/47ed23f7-4b2c-4844-82ff-a53220533359.dat", mode="rb") as plr:
#     strm = Stream(plr.read())

#     data = nbt.parse_nbt(strm)
#     data.print()

# with gzip.open(WORLD_FOLDER + "level.dat", mode="rb") as level:
#     strm = stream.Stream(level.read())
#     data = nbt.parse_nbt(strm)
#     data.print()

with open(WORLD_FOLDER + "region/r.0.0.mca", mode="rb") as region:
    locations = list(filter(
        lambda x: x[0] > 0,
        [
            [
                int.from_bytes(region.read(3), byteorder='big', signed=False) * 4096, 
                int.from_bytes(region.read(1), byteorder='big', signed=False) * 4096
            ] for i in range(1024)
        ]
    ))

    timestamps = region.read(4096)

    for loc in locations:
        region.seek(loc[0])
        datalen = int.from_bytes(region.read(4), byteorder='big', signed=False)
        compr = region.read(1)
        decompressed = zlib.decompress(region.read(datalen))
        with open("workrng.nbt", mode="wb") as wrk:
            wrk.write(decompressed)
        data = nbt.parse_nbt(stream.Stream(decompressed))
        # data.print()

# with open("workrgn.nbt", mode="rb") as workfile:
#     data = nbt.parse_nbt(workfile)
#     data.print()
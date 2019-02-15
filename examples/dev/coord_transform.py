from rtools import geom_conv

coords = [
    (296153.369,7137678.937),
    (296203.959,7137570.986),
    (296256.938,7137645.476)
]

conv = geom_conv(32638)
print conv.coords_reproj(4326, *coords)
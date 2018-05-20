from raster_tools import raster2array, raster2transform
from matplotlib import pyplot as plt

in_raster = "input.tif"
out_raster = "output.tif"

_in = in_raster

_in = raster2transform(_in, 455, 314)
print _in.cols
print _in.rows
# show in matplotlib
plt.title("show")
plt.imshow(_in.array(), cmap='gray')
plt.show()

_in = raster2transform(_in, 225, 157)
print _in.cols
print _in.rows
# show in matplotlib
plt.title("show")
plt.imshow(_in.array(), cmap='gray')
plt.show()

_in = raster2transform(_in, 3000, 3000)
print _in.cols
print _in.rows
# show in matplotlib
plt.title("show")
plt.imshow(_in.array(), cmap='gray')
plt.show()
_in.save(out_raster)

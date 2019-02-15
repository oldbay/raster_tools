
from rtools import geom_conv
import osr

_shp_file = 'shp/mask_4326.shp'
_shp_epsg = 4326
#_shp_file = 'shp/mask_28410.shp'
#_shp_epsg = 28410


_gc = geom_conv(28410)
print _gc.get_layer_extent()
_gc.shp_file2layer(_shp_file, 0, _shp_epsg)
print _gc.get_layer_extent()
_gc.Projection = 4326
_gc.layer_reproj()
print _gc.get_layer_extent()

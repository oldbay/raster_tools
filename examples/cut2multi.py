from rtools import raster2array, array2raster, raster2multi
import ogr

raster_file = "multiraster.tif"
shp_file = "points_array.shp"

# read from chennels
raster1 = raster2array(raster_file, 1)
raster2 = raster2array(raster_file, 2)
raster3 = raster2array(raster_file, 3)

# read shp file
_shp = ogr.Open(shp_file, update=1)
layer = _shp.GetLayerByIndex(0)

# add points for cut
point = []
for i in range(layer.GetFeatureCount()):
    geometry = layer.GetFeature(i)
    x, h, y, h = geometry.GetGeometryRef().GetEnvelope()
    point.append((float(x), float(y)))

# save cut to multi geotiff
raster2multi(
    "multi.tif",
    array2raster(raster1, raster1.cut_area(point)),
    array2raster(raster2, raster2.cut_area(point)),
    array2raster(raster3, raster3.cut_area(point)),
    # "MEM"
    # "GTiff"
)

from rtools import raster2array, array2raster

raster_file = "raster.tif"
shp_file = "shp_cut/cut.shp"

raster = raster2array(raster_file, 1)
array2raster(None, raster.cut_shp_file(shp_file), "cut.tif")

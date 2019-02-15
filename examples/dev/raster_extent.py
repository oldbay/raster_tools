
from osgeo import ogr
from rtools import raster2array, array2raster


ex_file = 'cut.tif'
cut_epsg = 4326
#cut_epsg = 28410
#cut_epsg = 32638
cut_file = 'forest.tif'
out_file = 'cut_extent.tif'

raster = raster2array(ex_file)
print raster.get_raster_extent(cut_epsg)
print raster.get_wgs84_area()
print raster.get_wgs84_area(pixel=True)
json = raster.get_raster_extent(cut_epsg, 'json')
wkt = raster.get_raster_extent(cut_epsg, 'wkt')
print wkt
print str(json)
ogr_geom = ogr.CreateGeometryFromJson(str(json))
print ogr_geom.ExportToWkt()


raster = raster2array(cut_file)
cut = raster.cut_ogr_geometry(wkt, 'wkt', cut_epsg)
array2raster(None, cut, out_file)

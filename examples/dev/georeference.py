
from rtools import (
    raster2array,
    array2raster, 
    raster2transform, 
    raster2multiraster, 
    multiraster2transform, 
    multiarray2multiraster
)
import osr

_in_file = 'test.jpg'
_in_file_gp = 'elev.tif'
_out_mask_file = 'out.tif'
_out_cut_file = 'cut.tif'
_out_mono_cut_file = 'monocut.tif'

_mask_shp_file = 'shp/mask_4326.shp'
#_mask_shp_file = 'shp/mask_28410.shp'

_cut_shp_file = 'shp/cut_4326.shp'

_raster_epsg = 28410
_shp_epsg = 4326
#_epsg = 28410


#raster = raster2array(_in_file_gp)
#raster.codage = 'uint8'
#raster.scale = True
#array2raster(raster, None, _out_mono_cut_file)



#raster = raster2transform(_in_file, None, None, _raster_epsg)
#raster.nodata = 0
#raster.codage = 'uint8'
#raster.scale = True
#raster.transform_shp_file(_mask_shp_file, 0, _shp_epsg)
#raster.save(_out_mono_cut_file)
#array2raster( 
    #None,
    #raster.cut_shp_file(
        #_cut_shp_file, 
        #0, 
        #_shp_epsg
    #), 
    #_out_mono_cut_file
#)

multi = multiraster2transform(_in_file, None, None, _raster_epsg)
#multi.codage = 'uint8'
#multi.codage = 'uint32'
#multi.scale = True
#multi.scale = (2, 253)
#multi.transform([40.77974, 64.30570], [40.78250, 64.30411])
multi.transform_shp_file(_mask_shp_file, 0, _shp_epsg)
multi.save(_out_mask_file)
multiarray2multiraster(
    _out_cut_file, 
    multi.cut_shp_file(
        _cut_shp_file, 
        0, 
        _shp_epsg
    ), 
)


#!/usr/bin/python2
# -*- coding: utf-8 -*-

from osgeo import gdal
import numpy as np
from config import GDAL_OPTS
from gdal_array import array2raster, raster2array, raster2transform
from vector_ops import proj_conv


class raster2multiarray (object):
    """
    Class for create multiarray
    
    multi - type:
     - None (default type)
     - cv (opencv type)
    codage - numpy array
     - np.float64 (default)
     - np.uint8 (for more operations opencv)
    bands_img - list objects raster2array
      - None - default
      - dict objects - create from self.create_bands_img
    """
    multi_type = None
    codage = np.float64
    bands_img = None

    def __init__(self, _fname, *args):
        """
        _fname - filename raster file
        if args[0] is list = bands list
        else args = bands list
        """
        self.fname = _fname
        if args == ():
            rcount = raster2array(self.fname, 1).Ds.RasterCount
            self.bands_num = range(1, rcount+1)
        elif type(args[0]) is list:
            self.bands_num = args[0]
        else:
            self.bands_num = args
            
    def create_bands_img(self):
        self.bands_img = []
        for band in self.bands_num:
            img = raster2array(self.fname, band)
            img.codage = self.codage
            self.bands_img.append(img)

    def array_reshape(_method):
        # step 1 - decorator for reshape array to multi_type
        def wrapper(self, *args, **kwargs):
            out = _method(self, *args, **kwargs)
            if type(out) is dict:
                _axis = out["array"].shape[0]
                _x = out["array"].shape[1]
                _y = out["array"].shape[2]
                if self.multi_type == "cv":
                    out["array"] = np.reshape(out["array"], (_x, _y, _axis))
                out["multi_type"] = self.multi_type
            else:
                _axis = out.shape[0]
                _x = out.shape[1]
                _y = out.shape[2]
                if self.multi_type == "cv":
                    out = np.reshape(out, (_x, _y, _axis))
            return out
        return wrapper

    def multibands(_method):
        # step 2 - decorator for create multibands array
        def wrapper(self, *args, **kwargs):
            _bands = []
            for band in self.bands_num:
                if self.bands_img is None:
                    img = raster2array(self.fname, band)
                    img.codage = self.codage
                else:
                    img = self.bands_img[band-1]
                _bands.append(
                    img.__class__.__dict__[_method.__name__](img, *args, **kwargs)
                )
            if type(_bands[0]) is dict:
                return {
                    "array": np.array([band["array"] for band in _bands]),
                    "shape": _bands[0]["shape"],
                    "transform": _bands[0]["transform"],
                    "projection": _bands[0]["projection"],
                    "nodata": _bands[0]["nodata"],
                }
            else:
                return np.array([band for band in _bands])
        return wrapper

    @array_reshape
    @multibands
    def array(self, *args, **kwargs):
        pass

    @array_reshape
    @multibands
    def get_std_dict(self, *args, **kwargs):
        pass

    @array_reshape
    @multibands
    def cut_area(self, *args, **kwargs):
        pass

    @array_reshape
    @multibands
    def cut_shp_layer(self, *args, **kwargs):
        pass

    @array_reshape
    @multibands
    def cut_shp_file(self, *args, **kwargs):
        pass

    @array_reshape
    @multibands
    def cut_ogr_geometry(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.array(*args, **kwargs)


class multiraster2transform (raster2multiarray):
    """
    Class for multiraster tranfsormation

    multi - type:
     - None (default type)
     - cv (opencv type)
    codage - numpy array
     - np.float64 (default)
     - np.uint8 (for more operations opencv)
    """
    multi_type = None
    codage = np.float64
    
    def __init__(self, _fname, _rows=None, _cols=None, _proj=None, *args):
        """
        _fname - filename raster file
        _rows - rows for transformation raster array
        _cols - cols for transformation raster array
        _proj - None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        if args[0] is list = bands list
        else args = bands list
        """
        # raster and bands numer init
        self.fname = _fname
        raster = raster2array(self.fname, 1)
        if args == ():
            rcount = raster.Ds.RasterCount
            self.bands_num = range(1, rcount+1)
        elif type(args[0]) is list:
            self.bands_num = args[0]
        else:
            self.bands_num = args
        # rows init
        if _rows is None:
            self.rows = raster.rows
        else:
            self.rows = _rows
        # cols init
        if _cols is None:
            self.cols = raster.cols
        else:
            self.cols = _cols
        # proj init
        if _proj is None:
            _proj = raster.Projection
        self.Projection = proj_conv(None, _proj).get_proj()
        # create list bands image
        self.create_bands_img()
    
    def create_bands_img(self):
        self.bands_img = []
        for band in self.bands_num:
            img = raster2transform(
                self.fname,
                self.rows, 
                self.cols, 
                self.Projection, 
                band
            )
            img.codage = self.codage
            self.bands_img.append(img)
   
    def multitransform(_method):
        # decorator for transformation multibands array
        def wrapper(self, *args, **kwargs):
            _bands = []
            for band in self.bands_num:
                img = self.bands_img[band-1]
                _bands.append(
                    img.__class__.__dict__[_method.__name__](img, *args, **kwargs)
                )
        return wrapper

    @multitransform
    def transform(self, *args, **kwargs):
        pass
   
    @multitransform
    def transform_shp_layer(self, *args, **kwargs):
        pass

    @multitransform
    def transform_shp_file(self, *args, **kwargs):
        pass

    @multitransform
    def transform_ogr_gemometry(self, *args, **kwargs):
        pass
    
    def save(self, _fname):
        raster2multiraster(_fname, *self.bands_img)

    # overloading raster2multiarray methods
    def array(self, *args, **kwargs):
        return raster2multiarray.array(self, *args, **kwargs)

    def get_std_dict(self, *args, **kwargs):
        return raster2multiarray.get_std_dict(self, *args, **kwargs)

    def cut_area(self, *args, **kwargs):
        return raster2multiarray.cut_area(self, *args, **kwargs)

    def cut_shp_layer(self, *args, **kwargs):
        return raster2multiarray.cut_shp_layer(self, *args, **kwargs)

    def cut_shp_file(self, *args, **kwargs):
        return raster2multiarray.cut_shp_file(self, *args, **kwargs)

    def cut_ogr_geometry(self, *args, **kwargs):
        return raster2multiarray.cut_ogr_geometry(self, *args, **kwargs)
    
    
class raster2multiraster (object):

    def __init__(self, _fname, *args):
        """
        args = list objets form array2raster or raster2array (band 1 only)
        args[-1] = drvname or default GTiff
        """
        self.fname = _fname
        if type(args[0]) is list:
            self.ext_rasters = args[0]
        else:
            self.ext_rasters = args
        if type(args[-1]) == str:
            self.drvname = args[-1]
        else:
            self.drvname = "GTiff"
        # test raster codage
        if 'raster_codage' in self.ext_rasters[0].__dict__:
            self.raster_codage = self.ext_rasters[0].raster_codage
        else:
            self.raster_codage = gdal.GDT_Float64
        # image size and tiles
        self.GeoTransform = self.ext_rasters[0].GeoTransform
        self.cols = self.ext_rasters[0].cols
        self.rows = self.ext_rasters[0].rows
        self.Projection = self.ext_rasters[0].Projection
        self._gdal_opts = self._gdal_test()
        drv = gdal.GetDriverByName(self.drvname)
        self.Ds = drv.Create(self.fname,
                             self.cols,
                             self.rows,
                             len(self.ext_rasters),
                             self.raster_codage,
                             options=self._gdal_opts)
        self.Ds.SetGeoTransform(self.GeoTransform)
        self.Ds.SetProjection(self.Projection)
        self.add_bands()

    def add_bands(self):
        _def_params = [
            self.GeoTransform,
            self.cols,
            self.rows,
            self.Projection,
        ]
        band_num = 1
        for _raster in self.ext_rasters:
            if type(_raster) != type(self.ext_rasters[0]):
                continue
            _raster_params = [
                _raster.GeoTransform,
                _raster.cols,
                _raster.rows,
                _raster.Projection,
            ]
            if _raster_params == _def_params:
                band = self.Ds.GetRasterBand(band_num)
                band.WriteArray(_raster.array())
                band.SetNoDataValue(_raster.nodata)
                band = None
            band_num += 1

    def _gdal_test(self):
        if self.drvname in GDAL_OPTS.keys():
            return GDAL_OPTS[self.drvname]
        else:
            return GDAL_OPTS['all']

    def __del__(self):
        self.Ds = None


class multiarray2multiraster(object):

    """
    input multiarray in unidict form
    """

    def __init__(self, _fanme, _mdict):
        self.fname = _fanme
        self.mdict = _mdict
        self._reshape()

    def _reshape(self):
        # reshape to cv
        if self.mdict["multi_type"] == "cv":
            _x = self.mdict["array"].shape[0]
            _y = self.mdict["array"].shape[1]
            _axis = self.mdict["array"].shape[2]
            self.mdict["array"] = np.reshape(
                self.mdict["array"], (_axis, _x, _y)
            )

    def save(self):
        # save multi dict to raster
        raster2multiraster(
            self.fname,
            [
                array2raster(
                    None,
                    {
                        "array": _band,
                        "shape": self.mdict["shape"],
                        "transform": self.mdict["transform"],
                        "projection": self.mdict["projection"],
                        "nodata": self.mdict["nodata"],
                    }
                )
                for _band
                in self.mdict["array"]
            ]
        )
   
    def __call__(self):
        self.save()
        
    def __del__(self):
        self.save()
    

class repair2reload (object):
    """
    test and reload raster of enside out
    this class is load memory!!!
    """

    def __init__(self, in_fname, out_fname=None, _drv="GTiff"):
        """
        in_fname = file name input raster
        out_fname = file name output raster, if None - to reload input raster
        _drv = driver raster file
        """
        self.in_fname = in_fname
        if out_fname is None:
            self.out_fname = in_fname
        else:
            self.out_fname = out_fname
        self.drvname = _drv
        self.repair()

    def repair(self):
        self.repair_bands = []
        band_first = raster2array(self.in_fname, 1)
        if False in band_first.is_valid():
            bands_count = band_first.Ds.RasterCount
            for _next in range(bands_count):
                band_num = _next + 1
                if band_num == 1:
                    self.repair_bands.append(
                        array2raster(
                            None,
                            band_first.repair()
                        )
                    )
                    del(band_first)
                else:
                    self.repair_bands.append(
                        array2raster(
                            None,
                            raster2array(self.in_fname, band_num).repair()
                        )
                    )

    def __del__(self):
        if self.repair_bands != []:
            raster2multi(self.out_fname, self.repair_bands, self.drvname)

#!/usr/bin/python2
# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr
import numpy as np
from config import GDAL_OPTS, raster_params, echo_output
from base64 import b64decode


class raster2array (object):
    """
    stdict_div - division output standart dict (False/Int - div)
                  for self.get_std_dict() & self.cut_area()
    codage - type numpy array returned to mrthods this class 
    """
    stdict_div = False
    codage = np.float64

    def __init__(self, fname, _band=1):

        self.Ds = gdal.Open(fname)
        # image size and tiles
        self.GeoTransform = self.Ds.GetGeoTransform()
        self.TL_x = float(self.GeoTransform[0])
        self.x_res = float(self.GeoTransform[1])
        self.x_diff = float(self.GeoTransform[2])
        self.TL_y = float(self.GeoTransform[3])
        self.y_res = float(self.GeoTransform[5])
        self.y_diff = float(self.GeoTransform[4])
        self.Projection = self.Ds.GetProjection()
        self.cols = self.Ds.RasterXSize
        self.rows = self.Ds.RasterYSize
        self.bands = self.Ds.RasterCount
        self.Band = self.Ds.GetRasterBand(_band)
        self.np_array = None

    def array(self, x_index=0, y_index=0, x_size=None, y_size=None):
        """
        return numpy array this raster for coordinates
        x_index - x index point np array
        y_index - y index point np array
        x_size - points for x axis
        y_size - points for y axis
        """
        if self.np_array is None:
            return self.Band.ReadAsArray(
                x_index,
                y_index,
                x_size,
                y_size
            ).astype(self.codage)
        else:
            if x_size is None:
                _cols = self.cols
            else:
                _cols = x_size

            if y_size is None:
                _rows = self.rows
            else:
                _rows = y_size

            return self.np_array[
                y_index:y_index+_rows,
                x_index:x_index+_cols
            ]
        
    def get_coord_index(self, x, y):
        """
        convert coordinate to numpy array index
        """
        # find x np array index
        x_index = int((x - self.TL_x) / self.x_res)
        if x_index >= self.cols:
            x_index = self.cols - 1
        if x_index < 0:
            x_index = 0
        # find y np array index
        y_index = int((y - self.TL_y) / self.y_res)
        if y_index >= self.rows:
            y_index = self.rows - 1
        if y_index < 0:
            y_index = 0
        return x_index, y_index

    def get_index_coord(self, x_index, y_index):
        """
        convert numpy array index to coordinate
        """
        # find x coordinate
        if x_index >= self.cols:
            x_index = self.cols
        if x_index < 0:
            x_index = 0
        x = float(self.TL_x + (x_index * self.x_res))
        # find y coordinate
        if y_index >= self.rows:
            y_index = self.rows
        if y_index < 0:
            y_index = 0
        y = float(self.TL_y + (y_index * self.y_res))
        return x, y

    def get_pixel_value(self, x, y):
        """
        return value raster pixel (numpy array data) from coordinte
        """
        x_index, y_index = self.get_coord_index(x, y)
        return float(
            self.array(x_index, y_index, 1, 1)[0, 0]
        )

    def iter_div(self, x_index, y_index, x_size, y_size, coord_x, coord_y):
        """
        iteration vision function
        """
        rows = range(
            0,
            y_size,
            int(y_size / self.stdict_div) + 1
        )
        cols = range(
            0,
            x_size,
            int(x_size / self.stdict_div) + 1
        )
        for row in rows:
            if rows.index(row) == len(rows) - 1:
                row_end = y_size
            else:
                row_end = rows[rows.index(row) + 1]
            for col in cols:
                if cols.index(col) == len(cols) - 1:
                    col_end = x_size
                else:
                    col_end = cols[cols.index(col) + 1]

                yield {
                    "array": self.array(
                        col+x_index, 
                        row+y_index,
                        col_end-col,
                        row_end-row
                        ),
                    "div": (row, row_end, col, col_end),
                    "shape": (y_size, x_size),
                    "transform": (
                        coord_x,
                        self.x_res,
                        self.x_diff,
                        coord_y,
                        self.y_diff,
                        self.y_res
                    ),
                    "projection": self.Projection,
                }
                
    def get_std_dict(self, x_index=0, y_index=0, x_size=None, y_size=None):
        """
        return standart dict for raster
        """
        if x_index != 0 or y_index != 0:
            UL_x, UL_y = self.get_index_coord(x_index, y_index)
        else:
            UL_x = self.TL_x
            UL_y = self.TL_y

        if x_size is not None:
            _cols = x_size
        else:
            _cols = self.cols

        if y_size is not None:
            _rows = y_size
        else:
            _rows = self.rows
       
        # output
        if self.stdict_div:
            return self.iter_div(x_index, y_index, _cols, _rows, UL_x, UL_y)
        else:
            return {
                "array": self.array(x_index, y_index, x_size, y_size),
                "shape": (_rows, _cols),
                "transform": (
                    UL_x,
                    self.x_res,
                    self.x_diff,
                    UL_y,
                    self.y_diff,
                    self.y_res
                ),
                "projection": self.Projection,
            }
        
    def cut_area(self, *args):
        """
        cut raster from more point coordinates
        args = [(x1,y1),(x2,y2),(xn,yn)] or (x1,y1),(x2,y2),(xn,yn)
        return to input array2raster class
        """
        if len(args) == 1 and type(args[0]) is list:
            args = args[0]
        x_array = [float(my[0]) for my in args]
        y_array = [float(my[1]) for my in args]
        UL_x = min(x_array)
        UL_y = max(y_array)
        LR_x = max(x_array)
        LR_y = min(y_array)
        UL_x_index, UL_y_index = self.get_coord_index(UL_x, UL_y)
        LR_x_index, LR_y_index = self.get_coord_index(LR_x, LR_y)
        x_size = LR_x_index - UL_x_index + 1
        y_size = LR_y_index - UL_y_index + 1
        return self.get_std_dict(UL_x_index, UL_y_index, x_size, y_size)

    def cut_shp_layer(self, layer):
        """
        Cut raster from bbox shp layer
        layer = ogr object laer
        return to input array2raster class
        """
        # reprojection layer
        layer_prj = layer.GetSpatialRef()
        raster_prj = osr.SpatialReference(wkt=self.Projection)
        if layer_prj != raster_prj:
            # BAD transform: sometimes incorect coordinates to reprojection - next testing
            transform = osr.CoordinateTransformation(layer_prj, raster_prj)
            drv = ogr.GetDriverByName("MEMORY")
            # create new vector layer
            source = drv.CreateDataSource('memData')
            out_layer = source.CreateLayer(
                'memData',
                geom_type=ogr.wkbPolygon,
                srs=raster_prj
            )
            # create field
            field = ogr.FieldDefn("mem", ogr.OFTString)
            out_layer.CreateField(field)
            # create feature
            for in_feature in layer:
                # transformed in feature
                transformed = in_feature.GetGeometryRef()
                transformed.Transform(transform)
                # creae out fature
                featureDefn = out_layer.GetLayerDefn()
                out_feature = ogr.Feature(featureDefn)
                out_feature.SetGeometry(transformed)
                out_feature.SetField("mem", "mem")
                out_layer.CreateFeature(out_feature)
                out_feature = None
            layer = out_layer
    
        x1, x2, y1, y2 = layer.GetExtent()
        if self.stdict_div:
            return self.cut_area((x1, y1), (x2, y2))
        else:
            cut_area = self.cut_area((x1, y1), (x2, y2))
            # rasterize layer mask
            shp_raster = array2raster(None, cut_area)
            gdal.RasterizeLayer(shp_raster.Ds, [1], layer, burn_values=[1])
            shp_cut_array = np.where(
                shp_raster.array() == 1, cut_area["array"], 0
            )
            return {
                "array": shp_cut_array,
                "shape": cut_area["shape"],
                "transform": cut_area["transform"],
                "projection": self.Projection,
            }

    def cut_shp_file(self, shp_file, shp_index=0):
        """
        Cut raster from bbox shape file
        shp_file = shapefile name
        shp_index = index layer from index
        return to input array2raster class
        """
        shp = ogr.Open(shp_file)
        layer = shp.GetLayerByIndex(shp_index)
        return self.cut_shp_layer(layer)

    def cut_ogr_geometry(self, _geom, _format="wkt", _geom_proj=None):
        """
        Cut raster from ogr polygon geometry:
        _geom = input geometry
        _format =:
            wkt - postgis geometry as ST_AsText() (DEFAULT)
            geojson
            gml
            wkb
        _geom_proj = None or projection in format osr.SpatialReference 
        return to input array2raster class
        """
        # crete vector in memory
        drv = ogr.GetDriverByName("MEMORY")
        source = drv.CreateDataSource('memData')
        if _geom_proj is None:
            srs_layer =  osr.SpatialReference(wkt=self.Projection)
        else:
            srs_layer = _geom_proj
        layer = source.CreateLayer(
            'memData',
            geom_type=ogr.wkbPolygon,
            srs=srs_layer
        )
        # create geometry
        if _format.lower() == "wkt":
            geom = ogr.CreateGeometryFromWkt(_geom)
        elif _format.lower() in ("geojson", "gjson", "json"):
            geom = ogr.CreateGeometryFromJson(_geom)
        elif _format.lower() == "gml":
            geom = ogr.CreateGeometryFromGML(_geom)
        elif _format.lower() == "wkb":
            geom = ogr.CreateGeometryFromWkb(b64decode(_geom))
        else:
            raise
        # create field
        field = ogr.FieldDefn("mem", ogr.OFTString)
        layer.CreateField(field)
        # create feature
        featureDefn = layer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(geom)
        feature.SetField("mem", "mem")
        layer.CreateFeature(feature)
        feature = None
        return self.cut_shp_layer(layer)

    def is_valid(self):
        """
        test valid np array for raster (this raster of enside out?)
        return (<x valid bool>, <y valid bool>)
        """
        test = [False, False]
        if self.TL_x > 0 and self.TL_y > 0:
            # EN
            if self.x_res > 0:
                test[0] = True
            if self.y_res < 0:
                test[1] = True
        elif self.TL_x > 0 and self.TL_y < 0:
            # ES
            if self.x_res > 0:
                test[0] = True
            if self.y_res > 0:
                test[1] = True
        elif self.TL_x < 0 and self.TL_y > 0:
            # WN
            if self.x_res < 0:
                test[0] = True
            if self.y_res < 0:
                test[1] = True
        elif self.TL_x < 0 and self.TL_y < 0:
            # WS
            if self.x_res < 0:
                test[0] = True
            if self.y_res > 0:
                test[1] = True
        return test

    def repair(self):
        """
        repair raster of enside out for x or/and y axis
        return to input array2raster class
        """
        test = self.is_valid()
        UL_x = self.TL_x
        UL_y = self.TL_y
        _x_res = self.x_res
        _y_res = self.y_res
        rep_array = self.array()
        if not test[0]:
            rep_array = np.array([my[::-1] for my in rep_array])
            UL_x = self.get_index_coord(self.cols, 0)[0]
            _x_res = -_x_res
        if not test[1]:
            rep_array = rep_array[::-1]
            UL_y = self.get_index_coord(0, self.rows)[1]
            _y_res = -_y_res
        # Fin
        return {
            "array": rep_array,
            "shape": (self.rows, self.cols),
            "transform": (
                UL_x,
                _x_res,
                self.x_diff,
                UL_y,
                self.y_diff,
                _y_res
            ),
            "projection": self.Projection,
        }

    def np_array_load(self):
        """
        load numpy array to self class (Load  memory)
        """
        if self.np_array is None:
            self.np_array = self.array()

    def np_array_clean(self):
        """
        clean numpy array from self class (Clean  memory)
        """
        self.np_array = None

    def __call__(self):
        return self.array()

    def __del__(self):
        self.Ds = None


class array2raster(raster2array):

    def __init__(self, _raster, _array, _fname=False, _band=1, _drv=False, _nodata=None):
        """
        _raster = oject to raster2array OR None
        _array = np.array OR standart dict
        _fname = filename OR False for use memory OR None
        _band = number of band
        _drv = driver raster file
        _nodata = nodata metadata for raster
        """

        self.fname = _fname
        self.drvname = _drv
        self._gdal_opts = self._gdal_test()
        # image size and tiles
        if type(_array) is dict:
            self.GeoTransform = _array["transform"]
            self.rows = _array["shape"][0]
            self.cols = _array["shape"][1]
            self.Projection = _array["projection"]
            _array = _array["array"]
        elif type(_array) is not dict and _raster is not None:
            self.GeoTransform = _raster.GeoTransform
            self.cols = _raster.cols
            self.rows = _raster.rows
            self.Projection = _raster.Projection
            if _array is None:
                _array = _raster.array()
        else:
            raise
        self.raster_codage = gdal.GDT_Float64
        drv = gdal.GetDriverByName(self.drvname)
        self.Ds = drv.Create(self.fname,
                             self.cols,
                             self.rows,
                             1,
                             self.raster_codage,
                             options=self._gdal_opts)
        self.Ds.SetGeoTransform(self.GeoTransform)
        self.Ds.SetProjection(self.Projection)
        self.Band = self.Ds.GetRasterBand(_band)
        if _array is not None:
            self.Band.WriteArray(_array)
        self.Band.FlushCache()
        if _nodata is not None:
            self.Band.SetNoDataValue(_nodata)
        # init rastre2array vars
        self.GeoTransform = self.Ds.GetGeoTransform()
        self.TL_x = float(self.GeoTransform[0])
        self.x_res = float(self.GeoTransform[1])
        self.x_diff = float(self.GeoTransform[2])
        self.TL_y = float(self.GeoTransform[3])
        self.y_res = float(self.GeoTransform[5])
        self.y_diff = float(self.GeoTransform[4])
        self.cols = self.Ds.RasterXSize
        self.rows = self.Ds.RasterYSize
        self.bands = self.Ds.RasterCount
        self.np_array = None

    def _gdal_test(self):
        if (not self.fname and not self.drvname) or (not self.fname and self.drvname):
            self.fname = ''
            self.drvname = 'MEM'
        elif self.fname and not self.drvname:
            self.drvname = 'GTiff'

        if self.drvname in GDAL_OPTS.keys():
            return GDAL_OPTS[self.drvname]
        else:
            return GDAL_OPTS['all']

    # overloading methods for use in raster2calc
    def get_std_dict(self, *args, **kwargs):
        return raster2array.get_std_dict(self, *args, **kwargs)

    def cut_area(self, *args, **kwargs):
        return raster2array.cut_area(self, *args, **kwargs)

    def cut_shp_layer(self, *args, **kwargs):
        return raster2array.cut_shp_layer(self, *args, **kwargs)

    def cut_shp_file(self, *args, **kwargs):
        return raster2array.cut_shp_file(self, *args, **kwargs)

    def cut_ogr_geometry(self, *args, **kwargs):
        return raster2array.cut_ogr_geometry(self, *args, **kwargs)

    def __call__(self):
        return self.Band

    def __del__(self):
        if echo_output and self.drvname != 'MEM':
            statistics = self.Band.GetStatistics(0, 1)
            print "Otupput raster: %s" % self.fname
            print "Metadata:"
            print "  STATISTICS_MAXIMUM=%s" % str(statistics[1])
            print "  STATISTICS_MEAN=%s" % str(statistics[2])
            print "  STATISTICS_MINIMUM=%s" % str(statistics[0])
            print "  STATISTICS_STDDEV=%s" % str(statistics[3])
        self.Band = None
        self.Ds = None


class raster2transform(raster2array):
    
    def __init__(self, _input, _cols, _rows, _proj=None):
        """
        _input is stdict (memory hight)
        _input is filename raster file (memory midi)
        _input is object raster2array (memory low)
        """
        if type(_input) is str:
            self.raster = raster2array(_input)
        elif type(_input) is dict:
            self.raster = array2raster(None, _input)
        else:
            self.raster = _input
        self.cols = _cols
        self.rows = _rows
        if _proj is None:
            self.Projection = self.raster.Projection
        else:
            self.Projection = _proj
        self.transform()

    def transform(self):
        # input params
        _cols = self.raster.cols
        _rows = self.raster.rows
        _GeoTransform = self.raster.GeoTransform
        _TL_x = float(_GeoTransform[0])
        _x_res = float(_GeoTransform[1])
        _x_diff = float(_GeoTransform[2])
        _TL_y = float(_GeoTransform[3])
        _y_res = float(_GeoTransform[5])
        _y_diff = float(_GeoTransform[4])
        # transform parms
        UL_x = _TL_x
        x_res = float((_x_res * _cols) / self.cols)
        x_diff = _x_diff
        UL_y = _TL_y
        y_diff = _y_diff
        y_res = float((_y_res * _rows) / self.rows)
        # create transform raster
        t_raster = array2raster(
            None,
            {
                "array": None, 
                #"array": np.zeros((self.rows, self.cols)), 
                "shape": (self.rows, self.cols),
                "transform": (
                    UL_x,
                    x_res,
                    x_diff,
                    UL_y,
                    y_diff,
                    y_res
                ),
                "projection": self.Projection,
            }
        )
        # transformation
        gdal.RegenerateOverviews(
            self.raster.Band,
            [t_raster.Band],
            'mode'
        )
        # reinit new value
        self.Ds = t_raster.Ds
        self.GeoTransform = self.Ds.GetGeoTransform()
        self.TL_x = float(self.GeoTransform[0])
        self.x_res = float(self.GeoTransform[1])
        self.x_diff = float(self.GeoTransform[2])
        self.TL_y = float(self.GeoTransform[3])
        self.y_res = float(self.GeoTransform[5])
        self.y_diff = float(self.GeoTransform[4])
        self.Projection = self.Ds.GetProjection()
        self.cols = self.Ds.RasterXSize
        self.rows = self.Ds.RasterYSize
        self.bands = self.Ds.RasterCount
        self.Band = self.Ds.GetRasterBand(1)
        self.np_array = None
        self.raster = None

    def save(self, _fname):
        array2raster(self, None, _fname)
        
    # overloading methods for use in raster2calc
    def get_std_dict(self, *args, **kwargs):
        return raster2array.get_std_dict(self, *args, **kwargs)

    def cut_area(self, *args, **kwargs):
        return raster2array.cut_area(self, *args, **kwargs)

    def cut_shp_layer(self, *args, **kwargs):
        return raster2array.cut_shp_layer(self, *args, **kwargs)

    def cut_shp_file(self, *args, **kwargs):
        return raster2array.cut_shp_file(self, *args, **kwargs)

    def cut_ogr_geometry(self, *args, **kwargs):
        return raster2array.cut_ogr_geometry(self, *args, **kwargs)


class raster2calc(object):
    
    def __init__(self, _div = 100):
        """
        _div = division raster
        """
        self.div = _div
    
    def calc_div(_method):
        # decorator for calculation division data
        def wrapper(self, math_fc, *args, **kwargs):
            """
            math_fc = lambda a, b: a + b
            *args = args for rastre2array.get_std_dict
            **kwargs = variables for lambda: a=1, b=2
            format lambda variables:
                stdict (memory hight)
                filename raster file (memory midi)
                object raster2array (memory low)
            """
            
            # convert lambda variables
            lambda_vars = []
            for key, value in kwargs.items():
                if type(value) is str:
                    kwargs[key] = raster2array(value)
                elif type(value) is dict:
                    kwargs[key] = array2raster(None, value)
                # create new variable in object for iteration method
                kwargs[key].stdict_div = self.div
                kwargs[key].divs = kwargs[key].__class__.__dict__[_method.__name__](
                    kwargs[key], *args
                ) 
                    
                if lambda_vars == []:
                    lambda_vars.append(key)
                    lambda_cols = kwargs[key].cols
                    lambda_rows = kwargs[key].rows
                else:
                    if kwargs[key].cols != lambda_cols or kwargs[key].rows != lambda_rows:
                        raise
                    else:
                        lambda_vars.append(key)
                    
            # calculation
            new_kwags = {}
            start_status = True
            while True:
                try:
                    for key in lambda_vars:
                        new_kwags[key] = kwargs[key].divs.next()
                        _div = new_kwags[key]["div"]
                        if start_status:
                            _shape = new_kwags[key]["shape"]
                            _transform = new_kwags[key]["transform"]
                            _projection = new_kwags[key]["projection"]
                            calc_array = np.zeros(_shape)
                            start_status = False
                        new_kwags[key] = new_kwags[key]["array"]
                except StopIteration:
                    break
                else:
                    calc_array[_div[0]:_div[1], _div[2]:_div[3]] = math_fc(**new_kwags)    
            return {
                "array": calc_array,
                "shape": _shape,
                "transform": _transform, 
                "projection": _projection,
            }
        return wrapper
   
    @calc_div 
    def get_std_dict(self, math_fc, *args, **kwargs):
        pass
    
    @calc_div 
    def cut_area(self, math_fc, *args, **kwargs):
        pass

    @calc_div 
    def cut_shp_layer(self, math_fc, *args, **kwargs):
        pass

    @calc_div 
    def cut_shp_file(self, math_fc, *args, **kwargs):
        pass

    @calc_div 
    def cut_ogr_geometry(self, math_fc, *args, **kwargs):
        pass
    
    def __call__(self, math_fc, *args, **kwargs):
        return self.get_std_dict(math_fc, *args, **kwargs)
#!/usr/bin/python2
# -*- coding: utf-8 -*-

from osgeo import gdal
import numpy as np
from config import (
    GDAL_OPTS, 
    raster_params, 
    echo_output,
    numpy_codage_type, 
    gdal2numpy_type, 
    numpy2gdal_type, 
    def_scale, 
    numpy_type2nodata
)
from vector_ops import proj_conv, geom_conv
try:
    from pyproj import Geod
except:
    Geod = None


class raster2array (geom_conv):
    """
    Class raster to array function
    
    stdict_div - division output standart dict (False/Int - div)
                  for self.get_std_dict() & self.cut_area()
    codage - type numpy array returned to mrthods this class
    sacle - scale to convert array (False,True,(min,max))
    nodata - raster nodata
    """
    stdict_div = False
    codage = np.float64
    scale = False
    nodata = -9999
    np_array = None

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
        self.return_band_codage()
        #self.return_band_nodata()
        
    def __setattr__(self, name, value):
        """
        Translate codage value to np.dtype type
        Correct nodata value from codage
        """
        if name == 'codage':
            _codage = numpy_codage_type(value)
            super(raster2array, self).__setattr__('codage', _codage)
            self.nodata = self.nodata
        elif name == 'nodata':
            _nodata = numpy_type2nodata(self.codage, value)
            super(raster2array, self).__setattr__('nodata', _nodata)
        else:
            super(raster2array, self).__setattr__(name, value)

    def return_band_nodata(self):
        self.nodata = self.Band.GetNoDataValue()

    def return_band_codage(self):
        self.codage = gdal2numpy_type[self.Band.DataType]

    def array(self, x_index=0, y_index=0, x_size=None, y_size=None):
        """
        return numpy array this raster for coordinates
        x_index - x index point np array
        y_index - y index point np array
        x_size - points for x axis
        y_size - points for y axis
        """
        if self.np_array is None:
            # read raster
            _rsater = self.Band.ReadAsArray(
                x_index,
                y_index,
                x_size,
                y_size
            )
            # find band nodata
            band_nodata = self.Band.GetNoDataValue()
            if band_nodata is None:
                band_nodata = np.nan
            # scale & band nodata
            if self.scale:
                if not (isinstance(self.scale, list) or isinstance(self.scale, tuple)):
                    self.scale = def_scale
                s_min = self.scale[0]
                s_max = self.scale[-1]
                s_meso = s_max - s_min
                r_max = np.max(np.where(_rsater==band_nodata, np.min(_rsater), _rsater))
                r_min = np.min(np.where(_rsater==band_nodata, np.max(_rsater), _rsater))
                r_meso = r_max - r_min
                _rsater = (((_rsater-r_min)*s_meso)/r_meso)+s_min
            else:
                _rsater = np.where(
                    _rsater==band_nodata, 
                    self.nodata, 
                    _rsater
                )
            # result
            return _rsater.astype(self.codage)
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
                    "nodata": self.nodata,
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
                "nodata": self.nodata,
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

    def cut_shp_layer(self, layer=None):
        """
        Cut raster from bbox shp layer
        layer = ogr object laer
        return to input array2raster class
        """
        if layer is not None:
            self.Layer = layer
            self.layer_reproj()
        x1, x2, y1, y2 = self.get_layer_extent()
        if self.stdict_div:
            return self.cut_area((x1, y1), (x2, y2))
        else:
            cut_area = self.cut_area((x1, y1), (x2, y2))
            # rasterize layer mask
            shp_raster = array2raster(None, cut_area)
            gdal.RasterizeLayer(shp_raster.Ds, [1], self.Layer, burn_values=[1])
            shp_cut_array = np.where(
                shp_raster.array() == 1, cut_area["array"], self.nodata
            )
            return {
                "array": shp_cut_array,
                "shape": cut_area["shape"],
                "transform": cut_area["transform"],
                "projection": self.Projection,
                "nodata": self.nodata,
            }

    def cut_shp_file(self, *args, **kwargs):
        """
        Cut raster from bbox shape file
        
        paramets for self.shp_file2layer
        ----------------------
        [0]shp_file = shapefile name
        [1]shp_index = index layer from index
        [2]_proj(describle) = None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        return to input array2raster class
        """
        self.shp_file2layer(*args, **kwargs)
        return self.cut_shp_layer()

    def cut_ogr_geometry(self, *args, **kwargs):
        """
        Cut raster from ogr polygon geometry:
        
        paramets for self.ogr_geometry2layer
        ----------------------
        [0]_geoms = input geometry or geometry list
        [1]_format =:
            wkt - postgis geometry as ST_AsText() (DEFAULT)
            geojson
            gml
            wkb
        [2]_proj = None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        return to input array2raster class
        """
        self.ogr_geometry2layer(*args, **kwargs)
        return self.cut_shp_layer()

    def is_georeferenced(self):
        if self.Projection == '' or self.TL_x == 0.0 or self.TL_y == 0.0:
            return False
        else:
            return True
        
    def get_raster_extent(self, proj, out=None):
        """
        return raster extent
        proj(describle) = None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        out None: list [[ul],[ur],[lr],[ll],[ul]] (list)
            wkt - wkt geometry polygon (str)
            json(geojson) - geojson geometry polygon (dict)
        """
        ul = self.get_index_coord(0, 0)
        ur = self.get_index_coord(0, self.rows)
        lr = self.get_index_coord(self.cols, self.rows)
        ll = self.get_index_coord(self.cols, 0)
        out_ret = self.coords_reproj(proj, ul, ur, lr, ll, ul)
        if isinstance(out, str) or isinstance(out, unicode):
            if out.lower() in ("geojson", "gjson", "json"):
                out_ret = {
                    "type": "Polygon",
                    "coordinates": [out_ret],
                }
                epsg = proj_conv(None, proj).get_proj('epsg')
                if epsg is not None:
                    out_ret["crs"] = {
                        "type": "name",
                        "properties": {"name": "EPSG:{}".format(epsg)}
                    }
            elif out.lower() == "wkt":
                out_ret = 'POLYGON (({0} {1},{2} {3},{4} {5},{6} {7},{8} {9}))'.format(
                        '{0:.13f}'.format(out_ret[0][0]),
                        '{0:.13f}'.format(out_ret[0][1]), 
                        '{0:.13f}'.format(out_ret[1][0]), 
                        '{0:.13f}'.format(out_ret[1][1]), 
                        '{0:.13f}'.format(out_ret[2][0]), 
                        '{0:.13f}'.format(out_ret[2][1]), 
                        '{0:.13f}'.format(out_ret[3][0]), 
                        '{0:.13f}'.format(out_ret[3][1]), 
                        '{0:.13f}'.format(out_ret[4][0]), 
                        '{0:.13f}'.format(out_ret[4][1]),
                )
        return out_ret
    
    def get_wgs84_area(self, pixel=False):
        if Geod is not None:
            g = Geod(ellps='WGS84')
            extent = self.get_raster_extent(4326)
            ul = extent[0]
            ur = extent[1]
            lr = extent[2]
            _, _, width = g.inv(ul[0], ul[1], ur[0], ur[1])
            _, _, height = g.inv(ur[0], ur[1], lr[0], lr[1])
            area = width * height
            if pixel:
                return area / (self.cols * self.rows)
            else:
                return area
            

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
            "nodata": self.nodata,
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
    """
    Class array to raster function
    """

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
        if isinstance(_array, dict):
            self.GeoTransform = _array["transform"]
            self.rows = _array["shape"][0]
            self.cols = _array["shape"][1]
            self.Projection = _array["projection"]
            self.nodata = _array["nodata"]
            _array = _array["array"]
        elif isinstance(_raster, raster2array):
            self.GeoTransform = _raster.GeoTransform
            self.cols = _raster.cols
            self.rows = _raster.rows
            self.Projection = _raster.Projection
            self.codage = _raster.codage
            self.nodata = _raster.nodata
            if not isinstance(_array, np.ndarray):
                _array = _raster.array()
        else:
            raise Exception('Array data type is wrong!')
        # correct codage and nodata to array numpy type
        if isinstance(_array, np.ndarray):
            self.codage = _array.dtype.type
        else:
            self.codage = np.float64
        self.nodata = numpy_type2nodata(self.codage, self.nodata)
        #create raster
        raster_codage = numpy2gdal_type(self.codage)
        drv = gdal.GetDriverByName(self.drvname)
        self.Ds = drv.Create(self.fname,
                             self.cols,
                             self.rows,
                             1,
                             raster_codage,
                             options=self._gdal_opts)
        self.Ds.SetGeoTransform(self.GeoTransform)
        self.Ds.SetProjection(proj_conv(None, self.Projection).get_proj())
        self.Band = self.Ds.GetRasterBand(_band)
        # write array
        if isinstance(_array, np.ndarray):
            self.Band.WriteArray(_array)
        self.Band.FlushCache()
        # insert nodata
        if _nodata is not None:
            self.nodata = _nodata
        if self.nodata is not None:
            self.Band.SetNoDataValue(self.nodata)
        # pyramid overviews
        #self.Ds.BuildOverviews("NEAREST", [2, 4, 8, 16, 32, 64])
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
        self.nodata = self.Band.GetNoDataValue()
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
    """
    Class for raster tranfsormation
    """

    def __init__(self, _input, _rows=None, _cols=None, _proj=None, _band=1):
        """
        _input - format for input:
            - is stdict (memory hight)
            - is filename raster file (memory midi)
            - is object raster2array (memory low)
        _rows - rows for transformation raster array
        _cols - cols for transformation raster array
        _proj - None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        """
        # Default raster2array values init
        self.stdict_div = raster2array.stdict_div
        self.codage = raster2array.codage
        self.scale = raster2array.scale
        self.nodata = raster2array.nodata
        self.np_array = raster2array.np_array
        # raster init
        if isinstance(_input, str) or isinstance(_input, unicode):
            self.raster = raster2array(_input, _band)
        elif isinstance(_input, dict):
            self.raster = array2raster(None, _input)
        elif isinstance(_input, raster2array) or isinstance(_input, array2raster):
            self.raster = _input
        else:
            raise Exception('error input format')
        # rows init
        if _rows is None:
            self.rows = self.raster.rows
        else:
            self.rows = _rows
        # cols init
        if _cols is None:
            self.cols = self.raster.cols
        else:
            self.cols = _cols
        # proj init
        if _proj is None:
            _proj = self.raster.Projection
        self.Projection = proj_conv(None, _proj).get_proj()
        # codage init
        self.return_band_codage()

    def return_band_nodata(self):
        self.nodata = self.raster.Band.GetNoDataValue()

    def return_band_codage(self):
        self.codage = gdal2numpy_type[self.raster.Band.DataType]

    def transform(self, *args):
        """
        georeference raster from more point coordinates
        args = [(x1,y1),(x2,y2),(xn,yn)] or (x1,y1),(x2,y2),(xn,yn)
        """
        if len(args) == 1 and type(args[0]) is list:
            args = args[0]
        # input params
        _cols = self.raster.cols
        _rows = self.raster.rows
        _GeoTransform = self.raster.GeoTransform
        _Projection = self.raster.Projection
        _TL_x = float(_GeoTransform[0])
        _x_res = float(_GeoTransform[1])
        _x_diff = float(_GeoTransform[2])
        _TL_y = float(_GeoTransform[3])
        _y_res = float(_GeoTransform[5])
        _y_diff = float(_GeoTransform[4])
        # test projection
        if self.Projection == '':
            raise Exception('projection for georeference not found')
        # transform parms
        if args == () and self.Projection == _Projection:
            UL_x = _TL_x
            UL_y = _TL_y
            LR_x = None
            LR_y = None
        elif args == () and self.Projection != _Projection:
            extent = self.raster.get_raster_extent(self.Projection)
            UL_x = extent[0][0]
            UL_y = extent[0][1]
            LR_x = extent[2][0]
            LR_y = extent[2][1]
        else:
            x_array = [float(my[0]) for my in args]
            y_array = [float(my[1]) for my in args]
            UL_x = min(x_array)
            UL_y = max(y_array)
            LR_x = max(x_array)
            LR_y = min(y_array)
        # find x_res 
        if _x_res == 1.0 and LR_x is None:
            raise Exception('coordinates for georeference not found')
        if LR_x is not None:
            x_res = float((LR_x - UL_x) / self.cols)
        else:
            x_res = float((_x_res * _cols) / self.cols)
        # find y_res 
        if _y_res == 1.0 and LR_y is None:
            raise Exception('coordinates for georeference not found')
        if LR_y is not None:
            y_res = float((LR_y - UL_y) / self.rows)
        else:
            y_res = float((_y_res * _rows) / self.rows)
        x_diff = _x_diff
        y_diff = _y_diff
        # create transform raster
        t_raster = array2raster(
            None,
            {
                "array": None,
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
                "nodata": self.nodata,
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
        self.raster = None
       
    def transform_shp_layer(self, layer=None):
        """
        Transform raster from bbox shp layer
        layer = ogr object laer
        """
        if layer is not None:
            self.Layer = layer
            self.layer_reproj()
        x1, x2, y1, y2 = self.get_layer_extent()
        return self.transform((x1, y1), (x2, y2))

    def transform_shp_file(self, *args, **kwargs):
        """
        Transform raster from bbox shape file
        
        paramets for self.shp_file2layer
        ----------------------
        [0]shp_file = shapefile name
        [1]shp_index = index layer from index
        [2]_proj(describle) = None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        """
        self.shp_file2layer(*args, **kwargs)
        return self.transform_shp_layer()
    
    def tranform_ogr_geometry(self, *args, **kwargs):
        """
        Transform raster from ogr polygon geometry:
        
        paramets for self.ogr_geometry2layer
        ----------------------
        [0]_geoms = input geometry or geometry list
        [1]_format =:
            wkt - postgis geometry as ST_AsText() (DEFAULT)
            geojson
            gml
            wkb
        [2]_proj = None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        """
        self.ogr_geometry2layer(*args, **kwargs)
        return self.transform_shp_layer()

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
            lambda_cols = None
            lambda_rows = None
            valid_class = (array2raster, raster2array, raster2transform)
            for key, value in kwargs.items():

                # convert str and dict to valid class
                if type(value) is str:
                    kwargs[key] = raster2array(value)
                elif type(value) is dict:
                    kwargs[key] = array2raster(None, value)

                # test object to valid classes
                if isinstance(kwargs[key], valid_class):
                    # create new variable in object for iteration method
                    kwargs[key].stdict_div = self.div
                    kwargs[key].divs = kwargs[key].__class__.__dict__[_method.__name__](
                        kwargs[key], *args
                    )

                    if lambda_cols is None and lambda_rows is None:
                        lambda_vars.append(key)
                        lambda_cols = kwargs[key].cols
                        lambda_rows = kwargs[key].rows
                    else:
                        if kwargs[key].cols != lambda_cols or kwargs[key].rows != lambda_rows:
                            raise
                        else:
                            lambda_vars.append(key)
                else:
                    lambda_vars.append(key)

            # calculation
            new_kwags = {}
            start_status = True
            while True:
                try:
                    for key in lambda_vars:
                        # test object to valid classes
                        if isinstance(kwargs[key], valid_class):
                            new_kwags[key] = kwargs[key].divs.next()
                            _div = new_kwags[key]["div"]
                            if start_status:
                                _shape = new_kwags[key]["shape"]
                                _transform = new_kwags[key]["transform"]
                                _projection = new_kwags[key]["projection"]
                                _nodata = new_kwags[key]["nodata"]
                                calc_array = np.zeros(_shape)
                                start_status = False
                            new_kwags[key] = new_kwags[key]["array"]
                        else:
                            new_kwags[key] = kwargs[key]
                except StopIteration:
                    break
                else:
                    calc_array[_div[0]:_div[1], _div[2]:_div[3]] = math_fc(**new_kwags)
            return {
                "array": calc_array,
                "shape": _shape,
                "transform": _transform,
                "projection": _projection,
                "nodata": _nodata,
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

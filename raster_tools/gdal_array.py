#!/usr/bin/python2
# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr
import numpy as np
from config import GDAL_OPTS, raster_params, echo_output
from base64 import b64decode


class raster2array (object):

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
        self.codage = gdal.GDT_Float64
        self.Band = self.Ds.GetRasterBand(_band)
        self.np_array = None

    def array(self, x_index=0, y_index=0, x_size=None, y_size=None):
        """
        return numpy array this raster for coordinates
        """
        if self.np_array is None:
            return self.Band.ReadAsArray(
                x_index,
                y_index,
                x_size,
                y_size
            ).astype(raster_params["nptype"])
        else:
            return self.np_array

    def np_array_load(self, _force=False):
        """
        load numpy array to self class (Load  memory)
        """
        if self.np_array is None and not _force:
            self.np_array = self.array()

    def np_array_clean(self):
        """
        clean numpy array from self class (Clean  memory)
        """
        self.np_array = None

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
            "np": (self.cols, self.rows),
            "transform": (UL_x, _x_res, self.x_diff, UL_y, self.y_diff, _y_res),
            "projection": self.Projection,
        }

    def get_pixel_value(self, x, y):
        """
        return value raster pixel (numpy array data) from coordinte
        """
        x_index, y_index = self.get_coord_index(x, y)
        if self.np_array is None:
            return float(
                self.array(x_index, y_index, 1, 1)[0, 0]
            )
        else:
            return float(
                self.np_array[y_index, x_index]
            )

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
        return {
            "array": self.array(UL_x_index, UL_y_index, x_size, y_size),
            "np": (x_size, y_size),
            "transform": (UL_x, self.x_res, self.x_diff, UL_y, self.y_diff, self.y_res),
            "projection": self.Projection,
        }

    def cut_shp_layer(self, layer):
        """
        Cut raster from bbox shp layer
        layer = ogr object laer
        return to input array2raster class
        """
        x1, x2, y1, y2 = layer.GetExtent()
        cut_area = self.cut_area((x1, y1), (x2, y2))
        shp_raster = array2raster(None, cut_area)
        gdal.RasterizeLayer(shp_raster.Ds, [1], layer, burn_values=[1])
        shp_cut_array = np.where(
            shp_raster.array() == 1, cut_area["array"], 0
        )
        return {
            "array": shp_cut_array,
            "np": cut_area["np"],
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

    def cut_ogr_geometry(self, postgis_geom, _format="wkt"):
        """
        Cut raster from ogr geometry:
        postgis_geom = input geometry
        _formati =:
            wkt - postgis geometry as ST_AsText() (DEFAULT)
            geojson
            gml
            wkb
        return to input array2raster class
        """
        # crete vector in memory
        drv = ogr.GetDriverByName("MEMORY")
        source = drv.CreateDataSource('memData')
        layer = source.CreateLayer(
            'memData',
            geom_type=ogr.wkbPolygon,
            srs=osr.SpatialReference(wkt=self.Projection)
        )
        # create geometry
        if _format.lower() == "wkt":
            geom = ogr.CreateGeometryFromWkt(postgis_geom)
        elif _format.lower() in ("geojson", "gjson", "json"):
            geom = ogr.CreateGeometryFromJson(postgis_geom)
        elif _format.lower() == "gml":
            geom = ogr.CreateGeometryFromGML(postgis_geom)
        elif _format.lower() == "wkb":
            geom = ogr.CreateGeometryFromWkb(b64decode(postgis_geom))
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

    def __call__(self):
        return self.array()

    def __del__(self):
        self.Ds = None


class array2raster(object):

    def __init__(self, _raster, _array, _fname=False, _band=1, _drv=False, _nodata=None):
        """
        _raster = oject to raster2array OR None
        _array = np.array OR dict of return raster2array.cut_area()
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
            self.cols = _array["np"][0]
            self.rows = _array["np"][1]
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
        self.codage = gdal.GDT_Float64
        drv = gdal.GetDriverByName(self.drvname)
        self.Ds = drv.Create(self.fname,
                             self.cols,
                             self.rows,
                             1,
                             self.codage,
                             options=self._gdal_opts)
        self.Ds.SetGeoTransform(self.GeoTransform)
        self.Ds.SetProjection(self.Projection)
        self.Band = self.Ds.GetRasterBand(_band)
        self.Band.WriteArray(_array)
        self.Band.FlushCache()
        if _nodata is not None:
            self.Band.SetNoDataValue(_nodata)

    def array(self):
        return self.Band.ReadAsArray().astype(raster_params["nptype"])

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


class raster2multi (object):

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
        # image size and tiles
        self.GeoTransform = self.ext_rasters[0].GeoTransform
        self.cols = self.ext_rasters[0].cols
        self.rows = self.ext_rasters[0].rows
        self.Projection = self.ext_rasters[0].Projection
        self.codage = self.ext_rasters[0].codage
        self._gdal_opts = self._gdal_test()
        drv = gdal.GetDriverByName(self.drvname)
        self.Ds = drv.Create(self.fname,
                             self.cols,
                             self.rows,
                             len(self.ext_rasters),
                             self.codage,
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
            self.codage,
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
                _raster.codage,
            ]
            if _raster_params == _def_params:
                band = self.Ds.GetRasterBand(band_num)
                band.WriteArray(_raster.array())
                band = None
            band_num += 1

    def _gdal_test(self):
        if self.drvname in GDAL_OPTS.keys():
            return GDAL_OPTS[self.drvname]
        else:
            return GDAL_OPTS['all']

    def __del__(self):
        self.Ds = None


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

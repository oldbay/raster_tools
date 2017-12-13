#!/usr/bin/python2
# -*- coding: utf-8 -*-

from osgeo import gdal
from config import GDAL_OPTS, raster_params, echo_output


class raster2array ():

    def __init__(self, fname, _band=1):

        self.Ds = gdal.Open(fname)
        # image size and tiles
        self.GeoTransform = self.Ds.GetGeoTransform()
        self.Projection = self.Ds.GetProjection()
        self.cols = self.Ds.RasterXSize
        self.rows = self.Ds.RasterYSize
        self.bands = self.Ds.RasterCount
        self.codage = gdal.GDT_Float32
        self.Band = self.Ds.GetRasterBand(_band)
        self.np_array = None

    def array(self):
        if self.np_array is None:
            return self.Band.ReadAsArray().astype(raster_params["nptype"])
        else:
            return self.np_array

    def np_array_load(self, _force=False):
        # load numpy array to self class (Load  memory)
        if self.np_array is None and not _force:
            self.np_array = self.array()

    def np_array_clean(self):
        # clean numpy array from self class (Clean  memory)
        self.np_array = None

    def get_array_index(self, x, y):
        TL_x, x_res, _, TL_y, _, y_res = self.GeoTransform
        x_index = int((x - TL_x) / x_res)
        y_index = int((y - TL_y) / y_res)
        return x_index, y_index

    def get_pixel_value(self, x, y):
        x_index, y_index = self.get_array_index(x, y)
        return float(self.array()[y_index, x_index])

    def __call__(self):
        return self.array()

    def __del__(self):
        self.Ds = None


class array2raster():

    def __init__(self, _raster, _array, _fname=False, _band=1, _drvname=False):

        self.fname = _fname
        self.drvname = _drvname
        self._gdal_opts = self._gdal_test()
        # image size and tiles
        self.GeoTransform = _raster.GeoTransform
        self.Projection = _raster.Projection
        drv = gdal.GetDriverByName(self.drvname)
        self.Ds = drv.Create(self.fname,
                             _raster.cols,
                             _raster.rows,
                             _raster.bands,
                             _raster.codage,
                             options=self._gdal_opts)
        self.Ds.SetGeoTransform(self.GeoTransform)
        self.Ds.SetProjection(self.Projection)
        self.Band = self.Ds.GetRasterBand(_band)
        self.Band.WriteArray(_array)
        self.Band.FlushCache()
        # self.Band.SetNoDataValue(raster_params["min"])

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

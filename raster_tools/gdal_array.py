#!/usr/bin/python2
# -*- coding: utf-8 -*-

from osgeo import gdal
import numpy as np

from config import GDAL_OPTS, raster_params, echo_output

class raster2array ():

    def __init__(self, fname):

        self.Ds = gdal.Open(fname)
        # image size and tiles
        self.GeoTransform = self.Ds.GetGeoTransform()
        self.Projection = self.Ds.GetProjection()
        self.cols  = self.Ds.RasterXSize
        self.rows  = self.Ds.RasterYSize
        self.bands = self.Ds.RasterCount
        self.codage = gdal.GDT_Float32
        self.array =  self.Ds.GetRasterBand(1).ReadAsArray().astype(raster_params["nptype"])

    def __del__(self):
        self.Ds = None

    def __call__(self):
        return self.array


class array2raster():

    def __init__(self, _raster, _array, fname):

        self.array = _array
        # image size and tiles
        self.GeoTransform = _raster.GeoTransform
        self.Projection = _raster.Projection
        drv = gdal.GetDriverByName("GTiff")
        self.fname = fname
        self.Ds = drv.Create(self.fname,
                        _raster.cols,
                        _raster.rows,
                        _raster.bands,
                        _raster.codage,
                        options=GDAL_OPTS)
        self.Band = self.Ds.GetRasterBand(1)

    def __del__(self):
        self.Band.WriteArray(self.array)
        self.Band.FlushCache()
        # self.Band.SetNoDataValue(raster_params["min"])
        if echo_output:
            statistics = self.Band.GetStatistics(0, 1)
            print "Otupput raster: %s"%self.fname
            print "Metadata:"
            print "  STATISTICS_MAXIMUM=%s"%str(statistics[1])
            print "  STATISTICS_MEAN=%s"%str(statistics[2])
            print "  STATISTICS_MINIMUM=%s"%str(statistics[0])
            print "  STATISTICS_STDDEV=%s"%str(statistics[3])
        self.Band = None
        self.Ds.SetGeoTransform(self.GeoTransform)
        self.Ds.SetProjection(self.Projection)
        self.Ds = None

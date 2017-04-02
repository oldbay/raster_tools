#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os, sys
import numpy as np

def calc(_file):

    from raster_tools import raster2array, array2raster
    path = os.path.dirname(_file)

    # Save spectr channels
    if "red.tif" in os.listdir(path):
        METADATA = raster2array("%s/red.tif"%path)
        RED = METADATA()
    else:
        print "Spectr raster '%s/red.tif' not found"%path
        sys.exit(1)
    if "nir.tif" in os.listdir(path):
        NIR = raster2array("%s/nir.tif"%path)()
    else:
        print "Spectr raster '%s/nir.tif' not found"%path
        sys.exit(1)

    # NDVI veg index from filter (remove negative variables in array)
    ndvi = (NIR - RED) / np.where((NIR + RED) == 0, 1, (NIR + RED))
    ndvi = np.where((ndvi != 1)&(ndvi > 0), ndvi, 0)
    print "NDVI"
    array2raster(METADATA, ndvi, path+"/index_ndvi.tif")
    del(ndvi)

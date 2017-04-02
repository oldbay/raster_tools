#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os, sys
import numpy as np

def calc(_file):

    from raster_tools import raster2array, array2raster
    path = os.path.dirname(_file)

    #Save spectr channels
    if "nir.tif" in os.listdir(path):
        METADATA = raster2array("%s/nir.tif"%path)
        NIR = METADATA()
    else:
        print "Spectr raster '%s/nir.tif' not found"%path
        sys.exit(1)
    if "swir1.tif" in os.listdir(path):
        SWIR1 = raster2array("%s/swir1.tif"%path)()
    else:
        print "Spectr raster '%s/swir1.tif' not found"%path
        sys.exit(1)

    #NDWI water index from filter (remove negative variables in array)
    ndwi = (SWIR1 - NIR) / np.where((SWIR1 + NIR) == 0, 1, (SWIR1 + NIR))
    ndwi = np.where((ndwi != 1)&(ndwi > 0), ndwi, 0)
    print "NDWI"
    array2raster(METADATA, ndwi, path+"/index_ndwi.tif")
    del(ndwi)

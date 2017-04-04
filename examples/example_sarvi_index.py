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

    if "blue.tif" in os.listdir(path):
        BLUE = raster2array("%s/blue.tif"%path)()
    else:
        print "Spectr raster '%s/blue.tif' not found"%path
        sys.exit(1)

    #sarvi Kaufman and Tanre (1994)
    a = 0.5
    Rb = RED - a * (RED - BLUE)
    L = 1 - ((2 * NIR + 1 - np.sqrt((2 * NIR + 1)**2 - 8 * (NIR * RED))) / 2)
    sarvi = ((NIR - Rb)/np.where((NIR + Rb) == 0, 1, (NIR + Rb))) * (1 + L)
    print "SARVI"
    array2raster(METADATA, sarvi, path+"/index_sarvi.tif")
    del(sarvi)

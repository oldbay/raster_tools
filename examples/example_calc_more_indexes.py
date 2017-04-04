#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np
from raster_tools import raster2array, array2raster


def calc_index(path):
    #Save metadata
    METADATA = raster2array(path+"/blue.tif")

    #Save spectr channels
    # BLUE = raster2array(path+"/blue.tif")()
    # GREEN = raster2array(path+"/green.tif")()
    RED = raster2array(path+"/red.tif")()
    NIR = raster2array(path+"/nir.tif")()
    SWIR1 = raster2array(path+"/swir1.tif")()
    # SWIR2 = raster2array(path+"/swir2.tif")()

    #NDVI veg index standart calculate
    ndvi = (NIR - RED) / (NIR + RED)
    print "Standart NDVI"
    array2raster(METADATA, ndvi, path+"/index_ndvi_standart.tif")
    del(ndvi)

    #NDVI veg index from filter (remove negative variables in array)
    ndvi = (NIR - RED) / np.where((NIR + RED) == 0, 1, (NIR + RED))
    ndvi = np.where((ndvi != 1)&(ndvi > 0), ndvi, 0)
    print "Filtred NDVI"
    array2raster(METADATA, ndvi, path+"/index_ndvi.tif")
    # del(ndvi)

    #NDWI water index standart calculate
    ndwi = (SWIR1 - NIR) / (SWIR1 + NIR)
    print "Standart NDWI"
    array2raster(METADATA, ndwi, path+"/index_ndwi_standart.tif")
    del(ndwi)

    #NDWI water index from filter (remove negative variables in array)
    ndwi = (SWIR1 - NIR) / np.where((SWIR1 + NIR) == 0, 1, (SWIR1 + NIR))
    ndwi = np.where((ndwi != 1)&(ndwi > 0), ndwi, 0)
    print "Filtred NDWI"
    array2raster(METADATA, ndwi, path+"/index_ndwi.tif")
    # del(ndwi)

    #разница NDVI и NDWI
    # vwdif = ndvi - ndwi
    # print "VWdiff"
    # array2raster(METADATA, vwdif, path+"/index_vwdif.tif")
    # vwdif_bug = np.where(vwdif < 0, -0.5, vwdif)
    # array2raster(METADATA, vwdif_bug, path+"/index_vwdif_bug.tif")

    #сумма NDVI и NDWI
    # vwsum = ndvi + ndwi
    # print "VWsum"
    # array2raster(METADATA, vwsum, path+"/index_vwsum.tif")

    #ТРАНСПИРАЦИОННЫЙ NDVI
    #----------------------
    #транспирационная маска
    tmask = ndwi * (ndvi + ndwi)
    print "TMask"
    # array2raster(METADATA, tmask, path+"/index_tmask.tif")
    del(ndwi)

    #транспирационный ndvi - tndvi
    tndvi = ndvi - tmask
    tndvi = np.where(tndvi > 0, tndvi, 0)
    print "TNDVI"
    array2raster(METADATA, tndvi, path+"/index_tndvi.tif")

    #median filter TNDVI
    #media_filter mode = constant, reflect, nearest, mirror
    # from scipy import ndimage
    # print "filter TNDVI"
    # ftndvi = ndimage.median_filter(tndvi, size = 2, mode = "reflect")
    # array2raster(METADATA, ftndvi, path+"/index_ftndvi.tif")

    #NDDI
    # nddi = (ndvi - ndwi) / np.where((ndvi + ndwi) == 0, 1, (ndvi + ndwi))
    # print "NDDI"
    # array2raster(METADATA, nddi, path+"/index_nddi.tif")

    #NBR (Normalized Burn Ratio)
    # nbr = (NIR - SWIR2) / np.where((NIR + SWIR2) == 0, 1, (NIR + SWIR2))
    # print "NBR"
    # array2raster(METADATA, nbr, path+"/index_nbr.tif")

    #sarvi Kaufman and Tanre (1994)
    # a = 0.5
    # Rb = RED - a * (RED - BLUE)
    # L = 1 - ((2 * NIR + 1 - np.sqrt((2 * NIR + 1)**2 - 8 * (NIR * RED))) / 2)
    # sarvi = ((NIR - Rb)/np.where((NIR + Rb) == 0, 1, (NIR + Rb))) * (1 + L)
    # print "SARVI"
    # array2raster(METADATA, sarvi, path+"/index_sarvi.tif")

    #sarvi2 Huete et al.(1997)
    # sarvi2 = (25 * (NIR - RED)) / (1 + NIR + (6 * RED) - (7.5 * BLUE))
    # print "SARVI2"
    # array2raster(METADATA, sarvi2, path+"/index_sarvi2.tif")


if __name__ == "__main__":
    import os, sys

    #First argument -  path to Geodata directory
    calc_index(os.path.abspath(sys.argv[1]))

#!/usr/bin/python2
# -*- coding: utf-8 -*-

import numpy as np

"""
Global configs
"""

GDAL_OPTS = ["COMPRESS=LZW",
             "INTERLEAVE=PIXEL",
             "TILED=YES",
             "SPARSE_OK=TRUE",
             "BIGTIFF=YES"]

raster_params = {
    "nptype": np.float,
    "min": 0,
    "max": 1,
}

cnls = {
    "LANDSAT_5": {
        "blue": {'cnum': '1', 'esun': 1983.0, 'c':False},
        "green": {'cnum': '2', 'esun': 1796.0, 'c':False},
        "red": {'cnum': '3', 'esun': 1536.0, 'c':False},
        "nir": {'cnum': '4', 'esun': 1031.0, 'c':False},
        "swir1": {'cnum': '5', 'esun': 220.0, 'c':False},
        "swir2": {'cnum': '7', 'esun': 83.44, 'c':False},
    },
    "LANDSAT_7": {
        "blue": {'cnum': '1', 'esun': 1997.0, 'c':False},
        "green": {'cnum': '2', 'esun': 1812.0, 'c':False},
        "red": {'cnum': '3', 'esun': 1533.0, 'c':False},
        "nir": {'cnum': '4', 'esun': 1039.0, 'c':False},
        "swir1": {'cnum': '5', 'esun': 230.8, 'c':False},
        "swir2": {'cnum': '7', 'esun': 84.9, 'c':False},
    },
    "LANDSAT_8": {
        "blue": {'cnum': '2', 'esun': False, 'const_esun': 2067.0, 'c':[0.00041, 0.97470]},
        "green": {'cnum': '3', 'esun': False, 'const_esun': 1893.0, 'c':[0.00289, 0.99779]},
        "red": {'cnum': '4', 'esun': False, 'const_esun': 1603.0, 'c':[0.00274, 1.00446]},
        "nir": {'cnum': '5', 'esun': False, 'const_esun': 972.6, 'c':[0.00004, 0.98906]},
        "swir1": {'cnum': '6', 'esun': False, 'const_esun': 245.0, 'c':[0.00256, 0.99467]},
        "swir2": {'cnum': '7', 'esun': False, 'const_esun': 79.72, 'c':[-0.00327, 1.02551]},
    },
}

#If False - use calculation with
#http://grass.osgeo.org/grass65/manuals/i.landsat.toar.html
#If True - use Konstant with
#http://www.gisagmaps.com/landsat-8-atco/
landsat8_const_esun = False

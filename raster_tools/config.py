#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os, sys
import importlib
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

horizon_telnet = {
    "host": "horizons.jpl.nasa.gov",
    "port": 6775,
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

# If False - use calculation with
# http://grass.osgeo.org/grass65/manuals/i.landsat.toar.html
# If True - use Konstant with
# http://www.gisagmaps.com/landsat-8-atco/
landsat8_const_esun = False

# Import scripts for calculate raster
calc_methods = {
    "landsat": importlib.import_module("raster_calc.landsat"),
    "ndvi": importlib.import_module("raster_calc.ndvi"),
    "ndwi": importlib.import_module("raster_calc.ndwi"),
}

# Data priority sun(horizont sol data), sat(data for satelite) .. next
data_priority = ['sun','sat']

# Echo output (True, False)
echo_output = False


# raplace default from config file
if "RASTER_TOOLS_CONF" in os.environ:
    _conf_name = os.path.realpath(os.environ["RASTER_TOOLS_CONF"])
    if os.path.basename(_conf_name) in os.listdir(os.path.dirname(_conf_name)):
        _module_dirname = os.path.dirname(_conf_name)
        _module_name = os.path.basename(_conf_name).split(".")[0]
        sys.path.append(_module_dirname)
        conf = importlib.import_module(_module_name)
        if "GDAL_OPTS" in conf.__dict__: GDAL_OPTS = conf.GDAL_OPTS
        if "raster_params" in conf.__dict__: raster_params = conf.raster_params
        if "horizon_telnet" in conf.__dict__: horizon_telnet = conf.horizon_telnet
        if "cnls" in conf.__dict__: cnls = conf.cnls
        if "landsat8_const_esun" in conf.__dict__: landsat8_const_esun = conf.landsat8_const_esun
        if "calc_methods" in conf.__dict__: calc_methods = conf.calc_methods
        if "data_priority" in conf.__dict__: data_priority = conf.data_priority
        if "echo_output" in conf.__dict__: echo_output = conf.echo_output

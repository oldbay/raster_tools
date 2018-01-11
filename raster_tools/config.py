#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os, sys
import importlib
import types
import numpy as np


"""
Global configs
"""

GDAL_OPTS = {
    'MEM': [
        "INTERLEAVE=PIXEL"
    ],
    'GTiff': [
        "COMPRESS=LZW",
        "INTERLEAVE=PIXEL",
        "TILED=YES",
        "SPARSE_OK=TRUE",
        "BIGTIFF=YES"
    ],
    'all': [],
}

raster_params = {
    "nptype": np.float,
    "min": 0,
    "max": 1,
}

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

        # find variables
        for var in locals().keys():
            if type(locals()[var]) != types.ModuleType and var[:1] != "_":
                if var in conf.__dict__:
                    if type(locals()[var]) == types.DictType:
                        for _key in conf.__dict__[var].keys():
                            locals()[var][_key] = conf.__dict__[var][_key]
                    else:
                        locals()[var] = conf.__dict__[var]

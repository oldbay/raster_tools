#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os, sys
import importlib
import types
import numpy as np
import gdal

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

def_scale = [2, 253]

gdal2numpy_type = {
    gdal.GDT_Unknown: np.float32,
    gdal.GDT_Byte: np.uint8,
    gdal.GDT_Byte: np.int8,
    gdal.GDT_UInt16: np.uint16,
    gdal.GDT_Int16: np.int16,
    gdal.GDT_UInt32: np.uint32,
    gdal.GDT_Int32: np.int32,
    gdal.GDT_Float32: np.float32,
    gdal.GDT_Float64: np.float64,
    gdal.GDT_CInt16: np.complex64,
    gdal.GDT_CInt32: np.complex64,
    gdal.GDT_CFloat32: np.complex64,
    gdal.GDT_CFloat64: np.complex128,
}

numpy2gdal_type_dict = {
    np.uint8: gdal.GDT_Byte,
    np.int8: gdal.GDT_Byte,
    np.uint16: gdal.GDT_UInt16,
    np.int16: gdal.GDT_Int16,
    np.uint32: gdal.GDT_UInt32,
    np.int32: gdal.GDT_Int32,
    np.float32: gdal.GDT_Float32,
    np.float64: gdal.GDT_Float64,
    np.complex64: gdal.GDT_CFloat32,
    np.complex128: gdal.GDT_CFloat64,
}

# Echo output (True, False)
echo_output = False

# functions
def numpy_codage_type(_codage):
    if isinstance(_codage, type):
        pass
    elif isinstance(_codage, np.ndarray):
        _codage = _codage.dtype.type
    elif isinstance(_codage, str) or isinstance(_codage, unicode):
        _codage = np.dtype(_codage).type
    else:
        _codage = False
    return _codage


def numpy2gdal_type(numpy_type):
    numpy_type = numpy_codage_type(numpy_type)
    if not numpy2gdal_type_dict.has_key(numpy_type):
        numpy_type = np.float64
        
    return numpy2gdal_type_dict[numpy_type]


def numpy_type2nodata(numpy_type, nodata):
    numpy_type = numpy_codage_type(numpy_type)
    if numpy_type:
        if 'int' in numpy_type.__name__:
            np_type_info = np.iinfo
        else:
            np_type_info = np.finfo
        np_max = np_type_info(numpy_type).max
        np_min = np_type_info(numpy_type).min
        if nodata > 0 and nodata > np_max:
            nodata = np_max
        elif nodata < 0 and nodata < np_min:
            nodata = np_min
    else:
        raise Exception('Not valid numpy type')
    return nodata




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

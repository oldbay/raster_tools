#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import numpy as np

from config import (
    horizon_telnet,
    cnls,
    landsat8_const_esun,
    data_priority
)
from parser import sun_parser, mtl_parser


class landsat_spec(object):

    def __init__(self, sat_id, cnl, mtl, sun):

        cnum = cnls[sat_id][cnl]['cnum']
        # EARTH_SUN_DISTANCE
        if sat_id == "LANDSAT_8" and data_priority.index('sat') < data_priority.index('sun'):
            self.d = float(mtl['IMAGE_ATTRIBUTES']['EARTH_SUN_DISTANCE'])
        else:
            self.d = sun['EARTH_SUN_DISTANCE']
        # SUN_AZIMUTH
        if data_priority.index('sat') < data_priority.index('sun'):
            self.s_azim = float(mtl['IMAGE_ATTRIBUTES']['SUN_AZIMUTH'])
        else:
            self.s_azim = sun['SUN_AZIMUTH']
        # SUN_ELEVATION
        if data_priority.index('sat') < data_priority.index('sun'):
            self.s_elev = float(mtl['IMAGE_ATTRIBUTES']['SUN_ELEVATION'])
        else:
            self.s_elev = sun['SUN_ELEVATION']
        self.fname = str(mtl['PRODUCT_METADATA']['FILE_NAME_BAND_'+cnum])[1:-1]
        self.gain = float(mtl['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_'+cnum])
        self.bias = float(mtl['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_'+cnum])
        self.qc_lmax = int(mtl['MIN_MAX_PIXEL_VALUE']['QUANTIZE_CAL_MAX_BAND_'+cnum])
        self.qc_lmin = int(mtl['MIN_MAX_PIXEL_VALUE']['QUANTIZE_CAL_MIN_BAND_'+cnum])
        self.lmax = float(mtl['MIN_MAX_RADIANCE']['RADIANCE_MAXIMUM_BAND_'+cnum])
        self.lmin = float(mtl['MIN_MAX_RADIANCE']['RADIANCE_MINIMUM_BAND_'+cnum])
        self.c = cnls[sat_id][cnl]['c']
        if cnls[sat_id][cnl]['esun']:
            self.esun = cnls[sat_id][cnl]['esun']
        elif landsat8_const_esun:
            self.esun = cnls[sat_id][cnl]['const_esun']
        else:
            # Calculate esun for Landsat 8
            # http://grass.osgeo.org/grass65/manuals/i.landsat.toar.html
            # Esun = (PI * d^2) * RADIANCE_MAXIMUM / REFLECTANCE_MAXIMUM
            rad_max = float(mtl['MIN_MAX_RADIANCE']['RADIANCE_MAXIMUM_BAND_'+cnum])
            ref_max = float(mtl['MIN_MAX_REFLECTANCE']['REFLECTANCE_MAXIMUM_BAND_'+cnum])
            self.esun = (np.pi * (self.d**2)) * rad_max / ref_max

        # print "chennel %s - ESUN=%s"%(cnl, out[cnl]['esun'])


class init(object):

    def __init__(self, sat_config):
        self.sat_config = sat_config


    def landsat(self):
        mtl = mtl_parser(os.path.abspath(self.sat_config))
        # data for horizon
        horizon_date = mtl['PRODUCT_METADATA']['DATE_ACQUIRED']
        horizon_time = mtl['PRODUCT_METADATA']['SCENE_CENTER_TIME'].split(".")[0]
        lat_list = [
            float(mtl['PRODUCT_METADATA']['CORNER_UL_LAT_PRODUCT']),
            float(mtl['PRODUCT_METADATA']['CORNER_UR_LAT_PRODUCT']),
            float(mtl['PRODUCT_METADATA']['CORNER_LL_LAT_PRODUCT']),
            float(mtl['PRODUCT_METADATA']['CORNER_LR_LAT_PRODUCT']),
        ]
        lat_center = min(lat_list) + (max(lat_list) - min(lat_list))/2
        lon_list = [
            float(mtl['PRODUCT_METADATA']['CORNER_UL_LON_PRODUCT']),
            float(mtl['PRODUCT_METADATA']['CORNER_UR_LON_PRODUCT']),
            float(mtl['PRODUCT_METADATA']['CORNER_LL_LON_PRODUCT']),
            float(mtl['PRODUCT_METADATA']['CORNER_LR_LON_PRODUCT']),
        ]
        lon_center = min(lon_list) + (max(lon_list) - min(lon_list))/2
        sun = sun_parser(
            horizon_telnet["host"],
            horizon_telnet["port"],
            horizon_date=horizon_date,
            horizon_time=horizon_time,
            lat_center=lat_center,
            lon_center=lon_center
        )
        sat_id = str(mtl['PRODUCT_METADATA']['SPACECRAFT_ID'])[1:-1]

        spectres = {}
        for cnl in cnls[sat_id].keys():
            spectres[cnl] = landsat_spec(sat_id, cnl, mtl, sun)

        return spectres

#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import numpy as np

from config import cnls, landsat8_const_esun
from parser import sun_parser, mtl_parser

class spectr():

    def __init__(self, sat_id, cnl, mtl, sun_delta):

        cnum = cnls[sat_id][cnl]['cnum']
        self.d = sun_delta[mtl['PRODUCT_METADATA']['DATE_ACQUIRED']]
        self.s_azim = float(mtl['IMAGE_ATTRIBUTES']['SUN_AZIMUTH'])
        self.s_elev = float(mtl['IMAGE_ATTRIBUTES']['SUN_ELEVATION'])
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
            #Calculate esun for Landsat 8
            #http://grass.osgeo.org/grass65/manuals/i.landsat.toar.html
            #Esun = (PI * d^2) * RADIANCE_MAXIMUM / REFLECTANCE_MAXIMUM
            rad_max = float(mtl['MIN_MAX_RADIANCE']['RADIANCE_MAXIMUM_BAND_'+cnum])
            ref_max = float(mtl['MIN_MAX_REFLECTANCE']['REFLECTANCE_MAXIMUM_BAND_'+cnum])
            self.esun = (np.pi * (self.d**2)) * rad_max / ref_max

        # print "chennel %s - ESUN=%s"%(cnl, out[cnl]['esun'])



def init(telfile, sunfule):

    mtl_file = os.path.abspath(telfile)
    sun_delta = sun_parser(os.path.abspath(sunfule))
    mtl = mtl_parser(mtl_file)
    sat_id = str(mtl['PRODUCT_METADATA']['SPACECRAFT_ID'])[1:-1]

    spectres = {}
    for cnl in cnls[sat_id].keys():
        spectres[cnl] = spectr(sat_id, cnl, mtl, sun_delta)

    return spectres

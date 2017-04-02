#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np

from raster_tools import raster2array, array2raster, spectres, raster_params

def dark(data):
    """
    DNmin - dark 1%
    """
    dataALL = int(np.sum(np.where(data > 0, data, 0)))
    data001 = int(dataALL * 0.0001)
    DNmin = 0
    step = 1000
    i = True
    while i:
        DNsum = np.sum(np.where((data <= DNmin)&(data > 0), data, 0))
        if DNsum > data001:
            DNmin -= step
            if step != 1:
                step /= 10
            else:
                i = False
        else:
            DNmin += step

    print "DN dark 0.01 = %s"%(DNmin)
    return DNmin


def toa_radiance(data, mtl):

    # DN to radiance conversion if we have a sensible DN

    #radiance to formula:
    #classical
    #Lλ = ((LMAXλ - LMINλ)/(QCALMAX-QCALMIN)) * (QCAL-QCALMIN) + LMINλ
    # L = (( mtl.lmax - mtl.lmin )/(mtl.qc_lmax - mtl.qc_lmin))*\
            # (data - mtl.qc_lmin) + mtl.lmin

    #[Thome et al., 1994; Lu etal., 2002]
    #Lλsat = DNcal × Gainλ + Baisλ
    L = data * mtl.gain + mtl.bias

    return L

def haze_mask(DNmin, mtl, Qz, Tz):
    """
    Land surface temperature retrieval from LANDSAT TM 5
    Jose ́ A. Sobrino , Juan C. Jime ́nez-Mun ̃oz, Leonardo Paolini
    """
    #classical
    #Lλmin = ((LMAXλ - LMINλ)/(QCALMAX-QCALMIN)) * (QCmin-QCALMIN) + LMINλ
    # Lmin = (( mtl.lmax - mtl.lmin )/(mtl.qc_lmax - mtl.qc_lmin))*\
            # (DNmin - mtl.qc_lmin) + mtl.lmin

    #[Thome et al., 1994; Lu etal., 2002]
    #Lλmin = DNmin × Gainλ + Baisλ
    Lmin = DNmin * mtl.gain + mtl.bias

    #L1% = (0.01 × cos(θz) × Tz × Eo) / (π × D^2)
    L1 = (0.01 * np.cos(Qz) * Tz * mtl.esun)/(np.pi * mtl.d**2)

    #Lp = Lmin - L1%
    Lp = Lmin - L1

    print "haze mask Lp = %s"%(Lp)
    return Lp


def dos_method(Lsat, Lp,  mtl, Qz, Tz):
    """
    Land surface temperature retrieval from LANDSAT TM 5
    Jose ́ A. Sobrino , Juan C. Jime ́nez-Mun ̃oz, Leonardo Paolini
    """
    #Psup = (π × (Lsat − Lp) × D^2)/( Eo × cos(θz) × Tz)
    Psup = (np.pi * (Lsat - Lp) * mtl.d**2)/(mtl.esun * np.cos(Qz) * Tz)

    return Psup


if __name__ == "__main__":

    mtl_file = os.path.abspath(sys.argv[1])
    mtl_path = os.path.dirname(mtl_file)

    bands_all = spectres.init(mtl_file)

    for band in bands_all.keys():

        #mtl data from band
        mtl = bands_all[band]

        #Solar zenith angle
        Qz = np.radians(90 - mtl.s_elev)

        #Tz
        Tz = np.cos(Qz)
        # Tz = 1

        #load raster object
        raster = raster2array(mtl_path+"/"+mtl.fname)

        # array from band
        data = raster()

        # Start math operations
        #----------------
        #Search data is outside the Range qc_lmin & qc_lmax
        # passer = np.logical_and( mtl.qc_lmin < data, data < mtl.qc_lmax )
        # data = np.where(passer, data, raster_params["min"])

        #min dark object 1%
        DNdark001 = dark(data)

        #haze mask
        HazeMask = haze_mask(DNdark001, mtl, Qz, Tz)

        # top of atmosphere refractance
        TOAR = toa_radiance(data, mtl)

        # atmosphere correction COST method
        DOS = dos_method(TOAR, HazeMask, mtl, Qz, Tz)

        #otmatch data to raster
        outmath = DOS

        #Use regression coofficient OLI -> ETM+
        #Continuity of Reflectance Data between Landsat-7 ETM+ and
        #Landsat-8 OLI, for Both Top-of-Atmosphere and Surface
        #Reflectance: A Study in the Australian Landscape
        #Neil Flood
        #ρETM+ = c0 + c1 ρOLI
        if mtl.c:
            outmath = mtl.c[0] + mtl.c[1] * outmath

        #saturated pixels (> 1)
        #http://www.ncl.ac.uk/tcmweb/bilko/module7/lesson3.pdf
        #Because the exoatmospheric reflectance ρ has a value
        #between 0 and 1, the output image will need to be a
        #floating point (32 bit image).
        mask = np.less_equal(outmath, raster_params["max"])
        outmath = np.choose(mask, (raster_params["max"], outmath))

        #save band to specter
        array2raster(raster, outmath, mtl_path+"/"+band+".tif")

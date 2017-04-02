#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os,sys
from raster_examples.calc_index import calc_index

if __name__ == "__main__":
    #First argument -  path to Geodata directory
    calc_index( os.path.abspath(sys.argv[1]))

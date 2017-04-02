#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import os

def helpmy():
    print """
    raster_tools_calc <calc method> <conf file> [<conf_file.py>]
    or
    env RASTER_TOOLS_CONF=<conf_file.py> raster_tools_calc <calc method> <conf file>
    conf_file.py - optionality
    """

def run():

    if len(sys.argv) < 3:
        helpmy()
        sys.exit(1)

    if len(sys.argv) == 4:
        _config = os.path.realpath(sys.argv[3])
        if os.path.basename(_config) in os.listdir(os.path.dirname(_config)):
            os.environ["RASTER_TOOLS_CONF"] = os.path.abspath(sys.argv[3])
        else:
            print "Config '%s' not found - use default!"%_config

    from raster_tools.config import calc_methods

    if sys.argv[1] in calc_methods.keys():
        _method = sys.argv[1]
        _file = _config = os.path.realpath(sys.argv[2])
        if os.path.basename(_file) in os.listdir(os.path.dirname(_file)):
            calc_methods[_method].calc(_file)
        else:
            print "Config file %s for method '%s' - not found"%(_file, _method)
    else:
        print "Calc method '%s' not found in config file"%sys.argv[1]
        sys.exit(1)

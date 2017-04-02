#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import os

def helpmy():
    print """
    calc_norm <sat type> <sat file> [<conf_file.py>]
    or
    env RASTER_TOOLS_CONF=<conf_file.py> calc_norm <sat type> <sat file>
    conf_file.py - optionality
    """


if __name__ == "__main__":

    if len(sys.argv) < 3:
        helpmy()
        sys.exit(1)

    if len(sys.argv) == 4:
        _config = os.path.realpath(sys.argv[3])
        if os.path.basename(_config) in os.listdir(os.path.dirname(_config)):
            os.environ["RASTER_TOOLS_CONF"] = os.path.abspath(sys.argv[3])
        else:
            print "Config '%s' not found - use default"%_config

    from raster_tools.config import norm_methods

    if sys.argv[1] in norm_methods.keys():
        _sat_type = sys.argv[1]
        _sat_file = _config = os.path.realpath(sys.argv[2])
        if os.path.basename(_sat_file) in os.listdir(os.path.dirname(_sat_file)):
            norm_methods[_sat_type].norm(_sat_file)
        else:
            print "Metadata for satelite '%s' file '%s' not found"%(_sat_type, _sat_file)
    else:
        print "Sat type '%s' not found in config file"%sys.argv[1]
        sys.exit(1)

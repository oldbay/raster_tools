#!/usr/bin/python2
# -*- coding: utf-8 -*-

import importlib

# Import scripts for calculate raster
calc_methods = {
    "sarvi": importlib.import_module("example_sarvi_index"),
}

# Echo output (True, False)
echo_output = True

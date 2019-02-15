#!/usr/bin/python2
# -*- coding: utf-8 -*-

import ogr
import osr
import numpy as np
import csv
from subprocess import Popen, PIPE

from raster_tools import raster2array


class comstring(object):

    def __init__(self):
        self.stdout_echo = False
        self.stderr_echo = False

    def run(self, cmd):
        _proc = Popen(
            cmd,
            shell=True,
            stdout=PIPE,
            stderr=PIPE
        )
        _res = _proc.communicate()
        _proc.wait()
        if _proc.returncode:
            print "ERR"
            if self.stderr_echo:
                print _res[1]
            return False
        else:
            if self.stdout_echo:
                print _res[0]
            print "OK"
            return True


def shp2vrt(shp_file, field_name, csv_file, vrt_file):
    # write CSV
    # загрузка shp файла
    _shp = ogr.Open(shp_file)
    layer = _shp.GetLayerByIndex(0)

    # обход циклом точек shp файла
    rows = []
    for geometry in layer:
        # определение координат точки векторного файла
        x, _, y, _ = geometry.GetGeometryRef().GetEnvelope()
        #
        data = geometry.GetField(field_name)
        rows.append([x, y, data])
    f = open(csv_file, 'w')
    _file = csv.writer(f, lineterminator='\n')
    _file.writerows(rows)
    f.close()

    # write VRT
    VRTFILE=[
    "<OGRVRTDataSource>\n",
    "    <OGRVRTLayer name=\"{}\">\n".format(field_name),
    "        <SrcDataSource>{}</SrcDataSource>\n".format(csv_file),
    "    <GeometryType>wkbPoint</GeometryType>\n",
    "    <GeometryField encoding=\"PointFromColumns\" x=\"field_1\" y=\"field_2\" z=\"field_3\"/>\n",
    "    </OGRVRTLayer>\n",
    "</OGRVRTDataSource>\n",
    ]
    f = open(vrt_file, 'w')
    f.writelines(VRTFILE)
    f.close()


def grid(in_raster, field_name, vrt_file, out_raster, div=1):
    # insert params
    _algo = "invdist:power=5:smoothing=4"
    _src_dc = raster2array(in_raster)
    _outsize = "{0} {1}".format(
        int(np.shape(_src_dc.array())[1]/div),
        int(np.shape(_src_dc.array())[0]/div)
    )
    _mathformat = str(_src_dc.array().dtype)
    raster_proj = osr.SpatialReference(wkt=_src_dc.Projection)
    _proj = "{0}:{1}".format(
        str(raster_proj.GetAttrValue("AUTHORITY", 0)),
        str(raster_proj.GetAttrValue("AUTHORITY", 1))
    )
    del(_src_dc)
    _geoformat = "GTiff"
    _logfile ="/tmp/grid.log"

    # strt utilite
    grid_cmd =[
        "gdal_grid",
        "-a {}".format(_algo),
        "-outsize {}".format(_outsize),
        "-a_srs {}".format(_proj),
        "-of {}".format(_geoformat),
        "-ot {}".format(_mathformat),
        "-l {}".format(field_name),
        vrt_file,
        out_raster,
        "--config NUM_THREADS ALL_CPUS"
        ">{} 2>&1".format(_logfile)
    ]
    cmd = comstring()
    print "Запуск gdal_grid - очень медленно!!!!, просмотр процесса в {}".format(_logfile)
    cmd.run(" ".join(grid_cmd))
    print "Завершение gdal_grid"


def grid_utils(raster_file, shp_file, field_name, out_dir):
    shp2vrt(
        shp_file,
        field_name,
        "{0}/{1}.csv".format(out_dir, field_name),
        "{0}/{1}.vrt".format(out_dir, field_name)
    )
    grid(
        raster_file,
        field_name,
        "{0}/{1}.vrt".format(out_dir, field_name),
        "{0}/{1}.tif".format(out_dir, field_name),
        10
    )

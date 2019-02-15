#! /usr/bin/python2
# -*- coding: utf-8 -*-

from rtools import raster2multiarray, multiarray2multiraster
from modules import psql

# загрузка растра в объект raster2array
in_file = "forest.tif"
out_dir = "rasters"

# установка параметров подключения в БД
dbhost = "localhost"
dbname = "dok_example"
dbuser = "gis"
dbpass = "gis"

# параметры поиска полигона в БД
geom_table = "crowns"

# запрос в БД возвращающий полигон в формате WKT
SQL = """
select ST_AsText(wkb_geometry)
from {}
""".format(geom_table)
_psql = psql(
    dbhost=dbhost,
    dbname=dbname,
    dbuser=dbuser,
    dbpass=dbpass
)
_psql.sql(SQL)
geoms = _psql.fetchall()
_psql.close()

raster_num = 1
raster = raster2multiarray(in_file)
raster.codage = 'uint8'
for geom in geoms:
    print raster_num, geom[0]
    std_dict = raster.cut_ogr_geometry(geom[0])
    multiarray2multiraster(
        '{0}/{1}.tif'.format(
            out_dir,
            raster_num
        ),
        std_dict
    ).save()
    raster_num += 1

#! /usr/bin/python2
# -*- coding: utf-8 -*-

from rtools import raster2array, array2raster
from modules import psql

# загрузка растра в объект raster2array
in_file = "result/calc.tif"
out_file = "result/cut_wkt.tif"

# установка параметров подключения в БД
dbhost = "localhost"
dbname = "dok_example"
dbuser = "gis"
dbpass = "gis"

# параметры поиска полигона в БД
geom_table = "crowns"
geom_ids = [
    55775,
    25879,
    29833,
    23443,
    57093
]

# запрос в БД возвращающий полигон в формате WKT
wkt_geoms = []
for geom_id in geom_ids:
    SQL = """
    select ST_AsText(wkb_geometry)
    from {0}
    where ogc_fid = {1}
    """.format(
        geom_table,
        geom_id
    )
    _psql = psql(
        dbhost=dbhost,
        dbname=dbname,
        dbuser=dbuser,
        dbpass=dbpass
    )
    _psql.sql(SQL)
    wkt_geoms.append(_psql.fetchone()[0])
    _psql.close()

#print wkt_geoms

# вырезание области растра по полигону WKT
# и сохранение в формате стандартного словаря
std_dict = raster2array(in_file).cut_ogr_geometry(wkt_geoms)

# сохранеие стандартного словаря в растр
array2raster(None, std_dict, out_file)

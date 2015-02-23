#!/usr/bin/python2
# -*- coding: utf-8 -*-

from pyparsing import (Word,
                       Suppress,
                       alphas,
                       nums)

"""
sun horison delta:
http://ssd.jpl.nasa.gov/horizons.cgi
-----------------------------------------------------------------
Ephemeris Type : OBSERVER
Target Body  :  Sun [Sol] [10]
Observer Location :  user defined ( 47°36'00.0''E, 48°30'36.0''N )
Time Span  :  Start=2006-01-01, Stop=2015-01-01, Step=1 d
Table Settings  :  QUANTITIES=20; object page=NO
Display/Output  :  download/save (plain text file)
-----------------------------------------------------------------

"""
months = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}

def mtl_parser(mtl_file):

    pos1 = Word(alphas + "_" + nums + alphas)
    pos2 = Word(alphas + '"' + nums + "_" + "." + "-" + "+")
    meso = Suppress("=")
    parser = pos1 + meso + pos2

    mtl = open(mtl_file, mode="r")

    mtl_lib = {}
    group = ""
    for line in mtl:
        if len(line.split("=")) == 2:
            parser_line = parser.parseString(line)

            if parser_line[0] == "GROUP" and parser_line[1] != "L1_METADATA_FILE":
                group = parser_line[1]
                mtl_lib[parser_line[1]] = {}

            elif parser_line[0] != "GROUP" and parser_line[0] != "END_GROUP":
                mtl_lib[group][parser_line[0]] = parser_line[1]

    mtl.close()
    return mtl_lib


def sun_parser(sun_file):

    sunfile = open(sun_file, mode="r")

    sun_delta = {}
    table = False
    for line in sunfile:

        if (line.find('$$EOE') >= 0):
            table = False

        if table:
            li = line.split(" ")
            li.remove('00:00')

            try:
                li.remove('A')
            except:
                pass
            try:
                li.remove('N')
            except:
                pass
            try:
                li.remove('m')
            except:
                pass
            try:
                li.remove('Am')
            except:
                pass
            try:
                li.remove('Nm')
            except:
                pass

            while True:
                try:
                    li.remove('')
                except:
                    break

            date = li[0].split("-")
            date[1] = months[date[1]]
            date = "-".join(date)

            sun_delta[date] = float(li[1])

        if (line.find('$$SOE') >= 0):
            table = True

    sunfile.close()

    return sun_delta

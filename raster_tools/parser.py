#!/usr/bin/python2
# -*- coding: utf-8 -*-

import telnetlib
from pyparsing import (Word,
                       Suppress,
                       alphas,
                       nums)

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


def sun_parser(host, port, **kwargs):

    _telnet = telnetlib.Telnet()
    _telnet.open(host, port)

    expect = ( ( r'Horizons>', 'Sun\n' ),
            ( r'Continue.*:', 'y\n' ),
            ( r'Select.*E.phemeris.*:', 'E\n'),
            ( r'Observe.*:', 'o\n' ),
            ( r'Coordinate center.*:', 'coord\n' ),
            ( r'Cylindrical or Geodetic input.*:', 'g\n' ),
            ( r'Specify geodetic.*:', '%s,%s,0.0000000\n'%(
                str(kwargs['lon_center']), str(kwargs['lat_center']))),
            ( r'Starting *UT.* :', '%s %s\n'%(
                str(kwargs['horizon_date']), str(kwargs['horizon_time']))),
            ( r'Ending *UT.* :', '%s 23:59:59\n'%str(kwargs['horizon_date'])),
            ( r'Output interval.*:', '1d\n' ),
            ( r'Accept default output.*:', 'y\n'),
            ( r'Select table quant.* :', '4,20\n' ),
            ( r'Scroll . Page: .*%', ' '),
            ( r'Select\.\.\. .A.gain.* :', 'X\n' )
    )

    while True:
        try:
            answer = _telnet.expect(list(i[0] for i in expect), 10)
        except EOFError:
            break
        else:
            if expect[answer[0]][1] == 'X\n':
                # output
                _cont = answer[2].split('\n')
                _pr = False
                for _c in _cont:

                    if _c.find('$$EOE') >= 0:
                        _pr = False
                        break

                    if _pr:
                        _out = _c.split(' ')
                        # delete emtpy
                        while True:
                            try:
                                _out.remove('')
                            except:
                                break
                        # print _out
                        # print [ float(my) for my in _out[-4:]]

                    if _c.find('$$SOE')>= 0:
                        _pr = True
            _telnet.write(expect[answer[0]][1])

    return {
        "SUN_AZIMUTH": float(_out[-4:][0]),
        "SUN_ELEVATION": float(_out[-4:][1]),
        "EARTH_SUN_DISTANCE": float(_out[-4:][2]),
    }

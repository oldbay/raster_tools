#!/usr/bin/python2
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
from random import randint


########################################################################
class proj_conv(object):
    """
    class for projections conversion operations
    """

    #----------------------------------------------------------------------
    def __init__(self, _obj=None, _proj=None):
        """
        _obj - input layer object for insert projection
        _proj - None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        """
        #init osr obj
        if _obj is not None:
            self.srs = _obj.GetSpatialRef()
        else:
            self.srs = osr.SpatialReference()
        #init base projection
        if _proj is not None:
            if isinstance(_proj, dict):
                if _proj != {}:
                    self.proj_type, self.proj_data = _proj.popitem()
                else:
                    raise Exception ('Projection dict is null')
            elif isinstance(_proj, str):
                if _proj != '':
                    self.proj_type = "Wkt"
                    self.proj_data = _proj
                else:
                    raise Exception ('Projection Wkt is null')
            elif isinstance(_proj, int):
                if _proj != 0:
                    self.proj_type = "EPSG"
                    self.proj_data = _proj
                else:
                    raise Exception ('Projection EPSG is null')
            else:
                raise Exception ('Unsupported projection format')
            self.set_proj()
            
    def set_proj(self, _proj_data=None, _proj_type=None):
        """
        formats:"EPSG", "EPSGA", "ERM", "ESRI",
                "MICoordSys", "Ozi", "PCI", 
                "Proj4", "URL", "USGS", "Wkt", 
                "XML"
        
        """
        # test projs
        if _proj_type is None:
            _proj_type = self.proj_type
        if _proj_data is None:
            _proj_data = self.proj_data
        # import proj
        if _proj_type.lower() == "epsg":
            self.srs.ImportFromEPSG(_proj_data)
        elif _proj_type.lower() == "epsga":
            self.srs.ImportFromEPSGA(_proj_data)
        elif _proj_type.lower() == "erm":
            self.srs.ImportFromERM(_proj_data)
        elif _proj_type.lower() == "ersi":
            self.srs.ImportFromESRI(_proj_data)
        elif _proj_type.lower() == "micoordsys":
            self.srs.ImportFromMICoordSys(_proj_data)
        elif _proj_type.lower() == "ozi":
            self.srs.ImportFromOzi(_proj_data)
        elif _proj_type.lower() == "pci":
            self.srs.ImportFromPCI(_proj_data)
        elif _proj_type.lower() == "proj4":
            self.srs.ImportFromProj4(_proj_data)
        elif _proj_type.lower() == "url":
            self.srs.ImportFromUrl(_proj_data)
        elif _proj_type.lower() == "usgs":
            self.srs.ImportFromUSGS(_proj_data)
        elif _proj_type.lower() == "wkt":
            self.srs.ImportFromWkt(_proj_data)
        elif _proj_type.lower() == "xml":
            self.srs.ImportFromXML(_proj_data)
        else:
            raise Exception('Projection type \'{}\' is not found'.format(_proj_type))
        
    def get_proj(self, _proj_type='wkt'):
        """
        formats:
            output: "MICoordSys", "PCI", "Proj4",
            "PrettyWkt", "USGS", "Wkt", "XML"
        """
        if _proj_type.lower() == "micoordsys":
            return self.srs.ExportToMICoordSys()
        elif _proj_type.lower() == "pci":
            return self.srs.ExportToPCI()
        elif _proj_type.lower() == "prettywkt":
            return self.srs.ExportToPrettyWkt()
        elif _proj_type.lower() == "proj4":
            return self.srs.ExportToProj4()
        elif _proj_type.lower() == "usgs":
            return self.srs.ExportToUSGS()
        elif _proj_type.lower() == "wkt":
            return self.srs.ExportToWkt()
        elif _proj_type.lower() == "xml":
            return self.srs.ExportToXML()
        
    def get_srs(self):
        return self.srs


########################################################################
class geom_conv(object):
    """
    class for geom conversion operations
    
    geom_type - default geometry type (polygon)
    """
    geom_type = ogr.wkbPolygon
    
    #----------------------------------------------------------------------
    def __init__(self, _proj=None):
        """
        Install self.Projection value
        """
        if _proj is not None:
            self.Projection = proj_conv(None, _proj).get_proj()
        else:
            self.Projection = ''
        
    def create_layer(self, srs, *args):
        # create name in memory
        mem_name = str(
            randint(
                100000000000000000000,
                999999999999999999999
            )
        )
        # create new vector layer
        drv = ogr.GetDriverByName("MEMORY")
        source = drv.CreateDataSource(mem_name)
        layer = source.CreateLayer(
            mem_name,
            geom_type=self.geom_type,
            srs=srs
        )
        # create field
        field = ogr.FieldDefn("mem", ogr.OFTString)
        layer.CreateField(field)
        # create features
        for feature in args:
            featureDefn = layer.GetLayerDefn()
            out_feature = ogr.Feature(featureDefn)
            out_feature.SetGeometry(feature)
            out_feature.SetField("mem", "mem")
            layer.CreateFeature(out_feature)
            out_feature = None
        #source and layer to self obj 
        self.Layer_source = source
        self.Layer = layer

    def layer_reproj(self, _layer=None):
        """
        Reprojection layer
        """
        # test null layer or projection
        if self.Projection == '' or not self.__dict__.has_key('Layer'):
            return None
        # test insert layer
        if _layer is None:
            layer = self.Layer
        else:
            layer = _layer
        # test projection layer
        layer_srs = proj_conv(layer).get_srs()
        raster_srs = proj_conv(None, self.Projection).get_srs()
        if layer_srs != raster_srs:
            # transform memory layers
            transform = osr.CoordinateTransformation(layer_srs, raster_srs)
            features = []
            for layer_feature in layer:
                wkt = layer_feature.GetGeometryRef().ExportToWkt()
                geom = ogr.CreateGeometryFromWkt(wkt)
                geom.Transform(transform)
                features.append(geom)
            self.create_layer(raster_srs, *features)

    def shp_file2layer(self, shp_file, shp_index=0, _proj=None):
        """
        Create layer from shape file
        
        shp_file = shapefile name
        shp_index = index layer from index
        _proj(describle) = None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        """
        shp = ogr.Open(shp_file)
        if shp is None:
            raise Exception('for \'{}\' shp file format not found'.format(shp_file))
        else:
            layer = shp.GetLayerByIndex(shp_index)
            if _proj is None:
                srs = proj_conv(layer).get_srs()
            else:
                srs = proj_conv(None, _proj).get_srs()
            # shp to memory layer
            features = []
            for layer_feature in layer:
                wkt = layer_feature.GetGeometryRef().ExportToWkt()
                geom = ogr.CreateGeometryFromWkt(wkt)
                features.append(geom)
            self.create_layer(srs, *features)
            # reprojection imput layer
            self.layer_reproj()

    def ogr_geometry2layer(self, _geoms, _format="wkt", _proj=None):
        """
        Create layer from ogr polygon geometry:
        _geoms = input geometry or geometry list
        _format =:
            wkt - postgis geometry as ST_AsText() (DEFAULT)
            geojson
            gml
            wkb
        _proj = None or projection in format: 
                str:WKT, int:EPSG, dict:{'proj_type':'proj_data'}
        """
        # geometry
        if not isinstance(_geoms, list):
            _ = []
            _.append(_geoms)
            _geoms = _
        # find projection
        if _proj is None and self.Projection == '':
            raise Exception('projection for geometry not found')
        elif _proj is None and self.Projection != '':
            _proj = {'wkt': self.Projection}
        srs = proj_conv(None, _proj).get_srs()
        # create features list
        features = []
        for _geom in _geoms:
            # create geometry
            if _format.lower() == "wkt":
                geom = ogr.CreateGeometryFromWkt(_geom)
            elif _format.lower() in ("geojson", "gjson", "json"):
                geom = ogr.CreateGeometryFromJson(_geom)
            elif _format.lower() == "gml":
                geom = ogr.CreateGeometryFromGML(_geom)
            elif _format.lower() == "wkb":
                geom = ogr.CreateGeometryFromWkb(b64decode(_geom))
            else:
                raise Exception("Format {} is not found".format(_format))
            features.append(geom)
        self.create_layer(srs, *features)
        # reprojection imput layer
        self.layer_reproj()

    def get_layer_extent(self):
        if self.__dict__.has_key('Layer'):
            return self.Layer.GetExtent()
        else:
            return None

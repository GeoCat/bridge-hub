import os
from osgeo import ogr
from .apiconstants import VECTORFILE, RASTERFILE, POSTGIS
from .files import temp_filename_in_temp_folder

def export_layer(source, sourcetype, fields):
    if sourcetype == VECTORFILE:
        name, ext = os.path.splitext(os.path.basename(source.lower()))
        isgpkg = ext == ".gpkg"
        if fields or not isgpkg:            
            if fields:
                pass #TODO add filter
            '''
            ogr.UseExceptions()
            input_datasource = ogr.GetDriverByName('ESRI Shapefile').Open(source)
            input_layer = input_datasource.GetLayerByIndex(0)

            output_filename = temp_filename_in_temp_folder(name + ".gpkg") 
            print(output_filename)
            output_datasource = ogr.GetDriverByName('GPKG').CreateDataSource(output_filename)

            output_layer = output_datasource.CreateLayer(name, input_layer.GetSpatialRef(), input_layer.GetGeomType())

            defn = input_layer.GetLayerDefn()
            for i in range(defn.GetFieldCount()):
                output_layer.CreateField(defn.GetFieldDefn(i))

            for feat in input_layer:
                output_layer.CreateFeature(feat)

            return output_filename

            '''
            input_layer = ogr.Open(source).GetLayerByIndex(0)            
            output_filename = temp_filename_in_temp_folder(name + ".gpkg")            
            out_ds = ogr.GetDriverByName('GPKG').CreateDataSource(output_filename)           
            out_layer = out_ds.CopyLayer(input_layer, name, [])            
            del input_layer, out_layer, out_ds
            return output_filename
            
        else:
            return source
    elif sourcetype == RASTERFILE:
        pass #TODO
    elif sourcetype == POSTGIS:
        pass #TODO
    else:
        return source
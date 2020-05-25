import os
from osgeo import ogr
from .apiconstants import VECTORFILE, RASTERFILE, POSTGIS
from .files import temp_filename_in_temp_folder

def export_layer(source, sourcetype, fields):
	if sourcetype == VECTORFILE:
		name, ext = os.path.splitext(source.lower())
		isgpkg = ext == ".gpkg"
		if fields or not isgpgk:			
			if fields:
				#TODO add filter
			input_layer = ogr.Open(in_shapefile).GetLayer()
		    driver = ogr.GetDriverByName('GPKG')
		    out_ds = driver.CreateDataSource(output_filename)
		    out_layer = out_ds.CopyLayer(input_layer)
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
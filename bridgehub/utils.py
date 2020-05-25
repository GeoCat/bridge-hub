from osgeo import ogr

def is_vector(filename):
	ds = ogr.Open(filename)
	if ds is None:
		return False
	isvector = ds.GetLayerCount() > 0
	del ds
	return isvector

def is_empty(filename):
	return False #TODO

def is_postgis(source):
	return False #TODO	

def layer_crs(source):
	ds = ogr.Open(source)
	layer = ds.GetLayer()
	ref = layer.GetSpatialRef()	
	code =  ref.GetAuthorityCode("PROJCS") or "4326"
	crs = "EPSG:" + code
	del ds
	return crs

def layer_extent(source):
	ds = ogr.Open(source)
	layer = ds.GetLayer()
	extent = layer.GetExtent()
	del ds
	return extent
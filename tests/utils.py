from osgeo import ogr

def get_fields(f):
    source = ogr.Open(f)
    layer = source.GetLayer()
    schema = []
    ldefn = layer.GetLayerDefn()
    for n in range(ldefn.GetFieldCount()):
        fdefn = ldefn.GetFieldDefn(n)
        schema.append(fdefn.name)
    return schema
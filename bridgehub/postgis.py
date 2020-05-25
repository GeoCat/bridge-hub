from .serverbase import ServerBase
from osgeo import ogr

class PostgisServer(ServerBase): 
    
    def __init__(self, name, host="localhost", port="5432", schema="public", database="db"):
        super().__init__()
        self.name = name
        self.host = host
        self.port = port
        self.schema = schema
        self.database = database

    @staticmethod
    def servertype():
        return "postgis"

    def import_layer(self, name, source, fields):
        if fields:
            #TODO
        else:
            connection_str = "PG:dbname='%s' host='%s' port='%s' user='%s' password='%s'" % (self.database, self.host, self.port, self.username, self.password)
            ogr.RegisterAll()
            pgds = ogr.Open(connection_str)
            ds = ogr.Open(source)
            layer = ds.GetLayerByIndex(0)        
            fullname = '"%s":"%s"' % (schema, name)
            pgds.CopyLayer(layer, fullname, [])


            

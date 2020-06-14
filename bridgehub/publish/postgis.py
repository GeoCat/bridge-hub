from .serverbase import ServerBase
from osgeo import ogr

class PostgisServer(ServerBase): 
    
    def __init__(self, host=None, port=None, schema=None, database=None):
        super().__init__()
        self.host = host or "localhost"
        self.port = port or "5432"
        self.schema = schema or "public"
        self.database = database or "db"

    @staticmethod
    def servertype():
        return "postgis"

    def import_layer(self, name, source):        
        ogr.RegisterAll()
        pgds = ogr.Open(self.gdal_connection_string())
        ds = ogr.Open(source)
        layer = ds.GetLayerByIndex(0)                
        pgds.CopyLayer(layer, name, ["OVERWRITE=YES"])

    def gdal_connection_string(self):
        return "PG:dbname='%s' host='%s' port='%s' user='%s' password='%s' schemas=%s" % (
                self.database, self.host, self.port, self.username, self.password, self.schema)        



            

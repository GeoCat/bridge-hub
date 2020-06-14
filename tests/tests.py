import os
import json
import context
import unittest
from bridgehub import api
from bridgehub.publish.geoserver import GeoserverServer
from webtest import TestApp
from utils import get_fields


GEOSERVER_URL = "http://localhost:8080/geoserver"
GEOSERVER_USERNAME = "admin"
GEOSERVER_PASSWORD = "geoserver"

GEONETWORK_URL = "https://localhost:8081/geonetwork"
GEONETWORK_USERNAME = "admin"
GEONETWORK_PASSWORD = "geonetwork"

POSTGIS_USERNAME = "tester"
POSTGIS_PASSWORD = "postgres"
POSTGIS_HOST = "localhost"
POSTGIS_PORT = "5432"
POSTGIS_DB = "pg_test"

def resource_path(name):
    return os.path.join(os.path.dirname(__file__), "data", name)

class BridgehubFunctionalTest(unittest.TestCase):

    def assertNoErrors(self, ret):
      dic = json.loads(ret.body)
      print(dic)
      for layer in dic["report"].values():
        self.assertTrue(layer["errors"] == [])

    def test_publish_data_from_geopackage(self):
        app = TestApp(api.app)
        server = {"servertype": "geoserver",
                  "username": GEOSERVER_USERNAME,
                  "password": GEOSERVER_PASSWORD,
                  "options":{
                    "url": GEOSERVER_URL
                  }}
        gpkg = resource_path("worldcountries.gpkg")
        geostyler_path = resource_path("worldcountries.geostyler")
        with open(geostyler_path) as f:
            geostyler = json.load(f)
        project = {"name": "test",
                   "groups":{},
                   "onlysymbology": False,
                   "servers":{                                
                                "data": server,
                                "metadata": None
                            },
                    "layers": [{
                                "sourcetype": "vectorfile",
                                "name": "test",
                                "data": {"sourcetype": "vectorfile",
                                         "source": gpkg},
                                "metadata": None,
                                "style": {
                                    "geostyler": geostyler,
                                    "icons": {}
                                },
                            }]
                   }
        ret = app.post("/publish", json.dumps(project))
        #self.assertNoErrors(ret)
        #TODO: assert correct result in server

    def test_publish_data_from_shapefile(self):
        app = TestApp(api.app)
        server = {"servertype": "geoserver",
                  "username": GEOSERVER_USERNAME,
                  "password": GEOSERVER_PASSWORD,
                  "options":{
                    "url": GEOSERVER_URL
                  }}
        shp = resource_path("worldcountries.shp")
        geostyler_path = resource_path("worldcountries.geostyler")
        with open(geostyler_path) as f:
            geostyler = json.load(f)
        project = {"name": "test",
                   "groups":{},
                   "onlysymbology": False,
                   "servers":{                                
                                "data": server,
                                "metadata": None
                            },
                    "layers": [{
                                "sourcetype": "vectorfile",
                                "name": "test",
                                "data": {"sourcetype": "vectorfile",
                                         "source": shp},
                                "metadata": None,
                                "style": {
                                    "geostyler": geostyler,
                                    "icons": {}
                                },
                            }]
                   }
        ret = app.post("/publish", json.dumps(project))
        self.assertNoErrors(ret)   
        #TODO: assert correct result in server

    def test_publish_data_to_postgis(self):
        app = TestApp(api.app)
        postgis = {"servertype": "postgis",
                  "username": POSTGIS_USERNAME,
                  "password": POSTGIS_PASSWORD,
                  "options":{
                    "database": POSTGIS_DB,
                    "host": POSTGIS_HOST,
                    "database": POSTGIS_DB,
                    "port": POSTGIS_PORT
                  }}        
        server = {"servertype": "geoserver",
                  "username": GEOSERVER_USERNAME,
                  "password": GEOSERVER_PASSWORD,
                  "options":{
                    "storage": GeoserverServer.POSTGIS_MANAGED_BY_BRIDGE,
                    "db": postgis,
                    "url": GEOSERVER_URL
                  }}
        gpkg = resource_path("worldcountries.gpkg")
        geostyler_path = resource_path("worldcountries.geostyler")
        with open(geostyler_path) as f:
            geostyler = json.load(f)
        project = {"name": "test_pg",
                   "groups":{},
                   "onlysymbology": False,
                   "servers":{
                                "data": server,
                                "metadata": None
                            },
                    "layers": [{                                
                                "name": "test_pg",
                                "data": {"sourcetype": "vectorfile",
                                         "source": gpkg},
                                "metadata": None,
                                "style": {
                                    "geostyler": geostyler,
                                    "icons": {}
                                },
                            }]
                   }
        ret = app.post("/publish", json.dumps(project))
        self.assertNoErrors(ret)
        #TODO: assert correct result in server

    def test_publish_data_using_original_postgis(self):
        app = TestApp(api.app)       
        server = {"servertype": "geoserver",
                  "username": GEOSERVER_USERNAME,
                  "password": GEOSERVER_PASSWORD,
                  "options":{
                    "use_original_data_source": True,
                    "url": GEOSERVER_URL
                  }}
        postgis = {"username": POSTGIS_USERNAME,
                   "password": POSTGIS_PASSWORD,
                   "host": POSTGIS_HOST,
                   "database": POSTGIS_DB,
                   "port": POSTGIS_PORT,
                   "table": '"public"."test"'}
        geostyler_path = resource_path("worldcountries.geostyler")
        with open(geostyler_path) as f:
            geostyler = json.load(f)
        project = {"name": "test_pg_direct",
                   "groups":{},
                   "onlysymbology": False,
                   "servers":{
                                "data": server,
                                "metadata": None
                            },
                    "layers": [{
                                "sourcetype": "postgis",
                                "name": "test",
                                "data": {"sourcetype": "postgis",
                                         "source": postgis},
                                "metadata": None,
                                "style": {
                                    "geostyler": geostyler,
                                    "icons": {}
                                },
                            }]
                   }
        ret = app.post("/publish", json.dumps(project))
        print(ret)
        #TODO: assert correct result in server

    def test_publish_metadata(self):
        app = TestApp(api.app)
        server = {"servertype": "geonetwork",
                  "username": GEONETWORK_USERNAME,
                  "password": GEONETWORK_PASSWORD,
                  "options":{
                    "url": GEONETWORK_URL
                  }}
        metadata = resource_path("test.mef")
        project = {"name": "test",
                   "groups":{},
                   "onlysymbology": False,
                   "servers":{                                
                                "data": None,
                                "metadata": server
                            },
                    "layers": [{
                                "sourcetype": None,
                                "name": "test",
                                "data": None,
                                "metadata": metadata,
                                "style": None
                            }]
                   }
        ret = app.post("/publish", json.dumps(project))
        self.assertNoErrors(ret)

if __name__ == '__main__':
    unittest.main()
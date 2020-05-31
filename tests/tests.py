import os
import json
import context
import unittest
from bridgehub import api
from bridgehub.geoserver import GeoserverServer
from webtest import TestApp
from utils import get_fields

def resource_path(name):
    return os.path.join(os.path.dirname(__file__), "data", name)

class BridgehubTest(unittest.TestCase):

    def NOTtest_add_server(self):
        app = TestApp(api.app)
        self.add_geoserver(app)
        ret = app.get("/servers")

    def NOTtest_layers(self):
        app = TestApp(api.app)
        self.add_geoserver(app)
        ret = app.get("/data/layers", {"project": "test", "server": "testgeoserver"})

    def test_publish_data_from_geopackage(self):
        app = TestApp(api.app)
        server = {"name": "testgeoserver",
                  "servertype": "geoserver",
                  "username": "admin",
                  "password": "geoserver",
                  "options":{
                    "url":"http://localhost:8080/geoserver"
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
                                "fields": {}
                            }]
                   }
        ret = app.post("/publish", json.dumps(project))
        print(ret)

    def test_publish_data_from_shapefile(self):
        app = TestApp(api.app)
        server = {"name": "testgeoserver",
                  "servertype": "geoserver",
                  "username": "admin",
                  "password": "geoserver",
                  "options":{
                    "url":"http://localhost:8080/geoserver"
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
                                "fields": {}
                            }]
                   }
        ret = app.post("/publish", json.dumps(project))
        print(ret)        

    def atest_publish_data_to_postgis(self):
        app = TestApp(api.app)
        postgis = {"name": "testpostgis",
                  "servertype": "postgis",
                  "username": "tester",
                  "password": "postgres",
                  "options":{
                    "database": "pg_test"
                  }}        
        server = {"name": "testgeoserver",
                  "servertype": "geoserver",
                  "username": "admin",
                  "password": "geoserver",
                  "options":{
                    "storage": GeoserverServer.POSTGIS_MANAGED_BY_BRIDGE,
                    "db": postgis,
                    "url":"http://localhost:8080/geoserver"
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
                                "name": "test",
                                "data": {"sourcetype": "vectorfile",
                                         "source": gpkg},
                                "metadata": None,
                                "style": {
                                    "geostyler": geostyler,
                                    "icons": {}
                                },
                                "fields": {}
                            }]
                   }
        ret = app.post("/publish", json.dumps(project))
        print(ret)

    def test_publish_data_using_original_postgis(self):
        app = TestApp(api.app)       
        server = {"name": "testgeoserver",
                  "servertype": "geoserver",
                  "username": "admin",
                  "password": "geoserver",
                  "options":{
                    "use_original_data_source": True,
                    "url":"http://localhost:8080/geoserver"
                  }}
        postgis = {"username": "tester",
                   "password": "postgres",
                   "host": "localhost",
                   "database": "pg_test",
                   "port": "5432",
                   "table": '"public"."test"'}
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
                                "sourcetype": "postgis",
                                "name": "test",
                                "data": {"sourcetype": "postgis",
                                         "source": postgis},
                                "metadata": None,
                                "style": {
                                    "geostyler": geostyler,
                                    "icons": {}
                                },
                                "fields": {}
                            }]
                   }
        ret = app.post("/publish", json.dumps(project))
        print(ret)



    '''
    def testToSld(self):
        with open(stylePath("style.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(api.app)
        ret = app.post("/convert/to/sld", {"style": geostyler})
        self.assertTrue(equalsOutputFile(ret, "style.sld"))    

    def testToMapbox(self):
        with open(stylePath("style.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(api.app)
        ret = app.post("/convert/to/mapbox", {"style": geostyler})
        self.assertTrue(equalsOutputFile(ret, "style.mapbox"))

    def testToMapserver(self):
        with open(stylePath("style.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(api.app)
        ret = app.post("/convert/to/mapserver", {"style": geostyler})
        self.assertTrue(equalsOutputFile(ret, "style.mapserver"))
        self.assertTrue(equalsOutputFile(ret, "symbols.mapserver"))

    def testWrongStyleEndpoint(self):
        with open(stylePath("style.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(api.app)
        ret = app.post("/convert/to/mystyle", {"style": geostyler}, expect_errors=True)
        self.assertEqual(ret.status_code, 404)

    def testWrongStyleRequest(self):
        app = TestApp(api.app)
        ret = app.post("/convert/to/sld", {"wrong": "THIS IS WRONG"}, expect_errors=True)
        self.assertEqual(ret.status_code, 400)

    def testWrongStyleContent(self):
        app = TestApp(api.app)
        ret = app.post("/convert/to/sld", {"style": '{"wrong": "wrong"}'}, expect_errors=True)
        self.assertEqual(ret.status_code, 500)        
    '''


if __name__ == '__main__':
    unittest.main()
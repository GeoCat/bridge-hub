import os
import context
import server
import unittest

from webtest import TestApp

def stylePath(name):
    return os.path.join(os.path.dirname(__file__), "data", name)

def equalsOutputFile(res, filename):
    fileContent = res.json["style"][filename]
    with open(stylePath(filename),) as f:
        reference = f.read()        
    return reference == fileContent

class BridgeServerTest(unittest.TestCase):

    def testToSld(self):
        with open(stylePath("style.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(server.app)
        ret = app.post("/convert/to/sld", {"style": geostyler})
        self.assertTrue(equalsOutputFile(ret, "style.sld"))    

    def testToMapbox(self):
        with open(stylePath("style.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(server.app)
        ret = app.post("/convert/to/mapbox", {"style": geostyler})
        self.assertTrue(equalsOutputFile(ret, "style.mapbox"))

    def testToMapserver(self):
        with open(stylePath("style.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(server.app)
        ret = app.post("/convert/to/mapserver", {"style": geostyler})
        self.assertTrue(equalsOutputFile(ret, "style.mapserver"))
        self.assertTrue(equalsOutputFile(ret, "symbols.mapserver"))

    def testWrongEndpoint(self):
        with open(stylePath("style.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(server.app)
        ret = app.post("/convert/to/mystyle", {"style": geostyler}, expect_errors=True)
        self.assertEqual(ret.status_code, 404)

    def testWrongRequest(self):
        app = TestApp(server.app)
        ret = app.post("/convert/to/sld", {"wrong": "THIS IS WRONG"}, expect_errors=True)
        self.assertEqual(ret.status_code, 400)

    def testWrongStyleContent(self):
        app = TestApp(server.app)
        ret = app.post("/convert/to/sld", {"style": '{"wrong": "wrong"}'}, expect_errors=True)
        self.assertEqual(ret.status_code, 500)        

    def testInfo(self):
        app = TestApp(server.app)
        ret = app.get("/info")
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.json["formats"], list(server.methods["to"].keys()))


if __name__ == '__main__':
    unittest.main()
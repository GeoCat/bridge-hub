import os
import context
from bridgeserver import server
import unittest

from webtest import TestApp

def stylePath(name):
    return os.path.join(os.path.dirname(__file__), "data", name)

def equalsOutputFile(s, reference):
    with open(stylePath("test.geostyler")) as f:
        style = f.read()
    return style == s

class BridgeServerTest(unittest.TestCase):

    def testToSld(self):
        with open(stylePath("test.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(server.app)
        ret = app.post("/convert/to/sld", {"style": geostyler})
        #self.assertTrue(equalsOutputFile(ret.json["style"], "test.sld"))

    def testWrongEndpoint(self):
        with open(stylePath("test.geostyler")) as f:
            geostyler = f.read()
        app = TestApp(server.app)
        ret = app.post("/convert/to/mystyle", {"geostyler": geostyler}, expect_errors=True)
        self.assertEqual(ret.status_code, 404)

    def testWrongStyleContent(self):
        app = TestApp(server.app)
        ret = app.post("/convert/to/sld", {"geostyler": "THIS IS WRONG"}, expect_errors=True)
        self.assertEqual(ret.status_code, 500)

    def testInfo(self):
        app = TestApp(server.app)
        ret = app.get("/info")
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(ret.json["formats"], list(server.methods["to"].keys()))


if __name__ == '__main__':
    unittest.main()
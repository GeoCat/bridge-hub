
from bridgehub.publish.geoserver import GeoserverServer
from bridgehub.publish.geonetwork import GeonetworkServer
from bridgehub.publish.postgis import PostgisServer

_servers = {}

classes = [GeoserverServer, PostgisServer, GeonetworkServer]

def class_from_server_type(servertype):
    for c in classes:
        if c.servertype() == servertype:
            return c

def server_from_definition(definition):
    if definition is None:
        return None
    servertype = definition["servertype"]
    clazz = class_from_server_type(servertype)
    server = clazz(**definition["options"])
    server.set_credentials(definition["username"], definition["password"])
    return server 

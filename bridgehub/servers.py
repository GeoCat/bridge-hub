from copy import deepcopy
from .geoserver import GeoserverServer
from .postgis import PostgisServer

_servers = {}

classes = [GeoserverServer, PostgisServer]

def class_from_server_type(servertype):
    for c in classes:
        if c.servertype() == servertype:
            return c

def server_definition(server):
    d = {k: v for k, v in server.__dict__.items() if not (k.startswith("_") or k == "name")}
    serverdef = {}
    serverdef["name"] = server.name
    serverdef["options"] = d
    username, password = server.get_credentials()
    serverdef["username"] = username
    serverdef["password"] = password
    serverdef["servertype"] = server.servertype()
    return serverdef

def servers():
    return [server_definition(v) for v in _servers.values()]

def server_from_name(name):
    if name is None:
        return None
    return _servers.get(name)

def server_from_definition(definition):
    if definition is None:
        return None
    servertype = definition["servertype"]
    clazz = class_from_server_type(servertype)
    options = deepcopy(definition["options"])
    options["name"] = definition["name"]
    server = clazz(**options)
    server.set_credentials(definition["username"], definition["password"])
    return server 

def add_server(server):
    _servers[server["name"]] = server_from_definition(server)

def delete_server(name):
    global _servers
    del _servers[name]


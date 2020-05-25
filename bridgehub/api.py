import json
import site
import traceback
from pathlib import Path
site.addsitedir(Path(__file__).resolve().parent / "bridgestyle")

from bridgehub.publish import publish_project
from bridgehub.config import ApiConfig
from bridgehub.servers import servers, add_server, delete_server, server_from_name
from bridgehub import data
from bottle import request, Bottle, HTTPResponse, response

app = Bottle()

def prepare_response(res):
    headers = {'Content-type': 'application/json'}
    return HTTPResponse(res, status=200, headers=headers)

def prepare_error_response(status, msg):
    headers = {'Content-type': 'application/json'}
    return HTTPResponse({'msg': msg}, status=status, headers=headers)

@app.error(500)
def custom500(error):
    response.content_type = 'application/json'
    return json.dumps({'msg': str(error)})

@app.get('/servers')
def getservers():
    headers = {'Content-type': 'application/json'} 
    return prepare_response({'servers': servers()})

@app.post('/servers')
def new_server():    
    body = request.body.read()
    serverdef = json.loads(body)
    name = serverdef["name"]
    server = server_from_name(name)
    if server is not None:
        return prepare_error_response(400, "A server with that name already exists")
    add_server(serverdef)

@app.put('/servers/{name}')
def update_server(name):
    body = request.body.read()
    serverdef = json.loads(body)
    serverdef["name"] = name
    add_server(serverdef)

@app.post('/publish')
def publish():
    project = request.body.read()
    res = publish_project(json.loads(project))
    return prepare_response(res)

@app.get('/data/layers')
def datalayers():    
    project = request.query.project
    server = request.query.server
    layers = data.layers(project, server)
    return prepare_response({"layers": layers})

@app.delete('/data/layers/{layer}')
def delete_layer(layer):    
    return prepare_response({})

############## Style conversion endpoints ###############

from bridgestyle import sld, mapboxgl, mapserver

conversion_modules = {
    "to": {
        "sld": sld.fromgeostyler,
        "mapbox": mapboxgl.fromgeostyler,
        "mapserver": mapserver.fromgeostyler
    },

    "from": {
        "sld": sld.togeostyler,
        "mapbox": mapboxgl.togeostyler,
        "mapserver": mapserver.togeostyler
    }
}

def prepare_conversion_response(direction, styleformat, res):
    headers = {'Content-type': 'application/json'}
    if direction == "to" and styleformat == "mapserver":
        style = {"style.mapserver": res[0],
                 "symbols.mapserver": res[1]}
    else:
        style = {"style.%s" % styleformat: res[0]}
    return HTTPResponse({'style': style, 'warnings': res[-1]},
                        status=200, headers=headers)

@app.post('/convert/<tofrom>/<styleformat>')
def convert(tofrom, styleformat):
    try:
        module = conversion_modules[tofrom][styleformat]
    except KeyError:
        return prepare_error_response(404, f"The specified conversion ({tofrom}/{styleformat}) is not available")

    try:
        original = request.forms.get('style')
        if tofrom == "to":
            original = json.loads(original)
    except:
        return prepare_error_response(400, traceback.format_exc())
    try:
        res = module.convert(original)
        return prepare_conversion_response(tofrom, styleformat, res)
    except Exception as e:
        return prepare_error_response(500, traceback.format_exc())





def main():
    settings = ApiConfig()
    app.run(host=settings.host, port=settings.port)


if __name__ == '__main__':
    main()

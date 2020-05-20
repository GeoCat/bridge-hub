import json
import os
import site
import traceback

from bottle import request, Bottle, HTTPResponse
from bottle_swagger import SwaggerPlugin

site.addsitedir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bridgestyle"))

from bridgehub.config import ApiConfig
from bridgehub.bridgestyle import sld, mapboxgl, mapserver


methods = {
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


def swagger_def():
    with open(os.path.join(os.path.dirname(__file__), "swagger.json")) as f:
        return json.load(f)


def prepare_response(direction, styleformat, res):
    headers = {'Content-type': 'application/json'}
    if direction == "to" and styleformat == "mapserver":
        style = {"style.mapserver": res[0],
                 "symbols.mapserver": res[1]}
    else:
        style = {"style.%s" % styleformat: res[0]}
    return HTTPResponse({'style': style, 'warnings': res[-1]},
                        status=200, headers=headers)


def prepare_error_response(status, msg):
    headers = {'Content-type': 'application/json'}
    return HTTPResponse({'message': msg}, status=status, headers=headers)


app = Bottle()
# app.install(SwaggerPlugin(swagger_def()))


@app.get('/info')
def info():
    try:
        headers = {'Content-type': 'application/json'}
        return HTTPResponse({"formats": list(methods['to'].keys())},
                            status=200, headers=headers)
    except Exception as e:
        return prepare_error_response(500, traceback.format_exc())


@app.post('/convert/<tofrom>/<styleformat>')
def convert(tofrom, styleformat):
    try:
        method = methods[tofrom][styleformat]
    except KeyError:
        return prepare_error_response(404, f"The specified conversion ({tofrom}/{styleformat}) is not available")

    try:
        original = request.forms.get('style')
        if tofrom == "to":
            original = json.loads(original)
    except:
        return prepare_error_response(400, traceback.format_exc())
    try:
        res = method.convert(original)
        return prepare_response(tofrom, styleformat, res)
    except Exception as e:
        return prepare_error_response(500, traceback.format_exc())


def main():
    settings = ApiConfig()
    app.run(host=settings.host, port=settings.port)


if __name__ == '__main__':
    main()

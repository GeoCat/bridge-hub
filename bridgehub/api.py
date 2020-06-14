import json
import traceback

from bridgehub.publish.publish import publish_project
from bridgehub.config import ApiConfig
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


@app.post('/publish')
def publish():
    project = request.body.read()
    res = publish_project(json.loads(project))
    return prepare_response(res)

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

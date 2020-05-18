import json
import os
import site
site.addsitedir(os.path.abspath(os.path.dirname(__file__) + "/bridgestyle"))

from .config import ApiConfig

from bottle import request, Bottle, response, HTTPResponse

from bridgestyle import sld, mapboxgl, mapserver

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

def prepare_response(style, warnings):
    response.headers['Content-Type'] = 'application/json'
    response.status = 200
    return json.dumps({'style': style,
                       'warnings': warnings})

def prepare_error_response(status, msg):
    headers = {'Content-type': 'application/json'}    
    raise HTTPResponse(json.dumps({'message': msg}), status=status, headers=headers)
    
app = Bottle()

@app.get('/info')
def info():
    try:        
        response.headers['Content-Type'] = 'application/json'
        ret = {"formats": list(methods['to'].keys())}
        response.status = 200
        return json.dumps(ret)
    except Exception as e:
        prepare_error_response(500, str(e))

@app.post('/convert/<tofrom>/<styleformat>')
def convert(tofrom, styleformat):
    try:
        method = methods[tofrom][styleformat]
    except KeyError:
        prepare_error_response(404, f"The specified conversion ({tofrom}/{styleformat}) is not available")

    geostyler = json.loads(request.forms.get('style'))
    try:
        style, warnings = sld.fromgeostyler.convert(geostyler)
        return prepare_response(style, warnings)
    except Exception as e:
        prepare_error_response(500, str(e))

def main():
    settings = ApiConfig()
    app.run(host=settings.host, port=settings.port)


if __name__ == '__main__':
    main()
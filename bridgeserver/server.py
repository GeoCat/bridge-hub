import json
import os
import site
import traceback
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

def prepare_response(tofrom, format, res):
    headers = {'Content-type': 'application/json'}
    if tofrom == "to" and format == "mapserver":
        style = {"style.mapserver": res[0],
                 "symbols.mapserver": res[1]}
    else:
        style = {"style.%s" % format: res[0]}
    return HTTPResponse(json.dumps({'style': style, 'warnings': res[-1]}), 
                       status=200, headers=headers)    

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
    
    try:
        original = request.forms.get('style')
        if tofrom == "to":
            original = json.loads(original)
        res = method.convert(original)
        return prepare_response(tofrom, styleformat, res)
    except Exception as e:
        prepare_error_response(500, traceback.format_exc())

def main():
    settings = ApiConfig()
    app.run(host=settings.host, port=settings.port)


if __name__ == '__main__':
    main()
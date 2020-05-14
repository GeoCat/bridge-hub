

from bottle import request, Bottle, response

app = Bottle()

@app.post('/convert/to/sld')
def convert():
    return "ok"
    
def main():
    settings = ApiConfig()
    app.run(host=settings.host, port=settings.port)

if __name__ == '__main__':
    main()
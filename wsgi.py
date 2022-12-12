from gevent import pywsgi
from compute import create_app

app = create_app()
if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()

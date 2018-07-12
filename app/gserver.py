from gevent.pywsgi import WSGIServer
from app import create_app
import os


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

server = WSGIServer(('', 80), app)
server.serve_forever()

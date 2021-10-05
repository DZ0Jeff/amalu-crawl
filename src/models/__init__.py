from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS


def init_app():
    app = Flask(__name__)
    CORS(app, expose_headers=["Content-Disposition"])
    return app


def init_socket(app):
    socketio = SocketIO(app, cors_allowed_origins="*")
    return socketio


app = init_app()
socketio = init_socket(app)
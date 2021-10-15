from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os


load_dotenv()

def init_app():
    app = Flask(__name__)
    CORS(app, expose_headers=["Content-Disposition"])
    return app


def init_socket(app):
    socketio = SocketIO(app, cors_allowed_origins="*")
    return socketio


def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1) # "postgresql://zqzqwesw:4ZKV5N8pFTIvhzJ5V0iDSW1Ks3vTIi_d@fanny.db.elephantsql.com/zqzqwesw"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db = SQLAlchemy(app)
    return db


app = init_app()
socketio = init_socket(app)
db = init_db(app)
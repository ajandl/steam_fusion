from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
# from environ_vars import environ_setup


# environ_setup()  # This shouldn't be needed now that .env is implemented.
app = Flask(__name__)
db = SQLAlchemy()
jwt = JWTManager()


def setup_app(app):
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)

    return app

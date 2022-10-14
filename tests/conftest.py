import pytest
from mixer.backend.flask import mixer

from app import app as flask_app
from app import db, routes, jwt  # noqa


DATABASE_TEST_URI = 'sqlite://'  # sqlite:memory ???

flask_app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_TEST_URI
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
flask_app.config['TESTING'] = True
flask_app.config['SECRET_KEY'] = 'thissecretkeyfortestingonly'
db.init_app(flask_app)
jwt.init_app(flask_app)


@pytest.fixture()
def app():
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.close()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def app_mixer(app):
    mixer.init_app(app)
    return mixer

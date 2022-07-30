from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    pw_hash = db.Column(db.Text, nullable=False)
    steamid = db.Column(db.Text)
    steam_name = db.Column(db.Text)
    user_creation_time = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        )

    entries = db.relationship('List_entry', backref='user')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def set_steam(self, steamid='', steam_name=''):
        self.steamid = steamid
        self.steam_name = steam_name


class Steam_game(db.Model):
    __tablename__ = 'steam_games'

    app_id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.Text, nullable=False)
    time_added = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    entries = db.relationship('List_entry', backref='app')


class List(db.Model):
    __tablename__ = 'lists'

    list_id = db.Column(db.Integer, primary_key=True, unique=True)
    list_name = db.Column(db.Text, nullable=False)
    creation_time = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    entries = db.relationship('List_entry', backref='list')


class List_entry(db.Model):
    __tablename__ = 'list_entries'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('app.id'), primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), primary_key=True)

    user = db.relationship('User', backref='entries')
    app = db.relationship('Steam_games', backref='entries')
    list = db.relationship('Lists', backref='entries')

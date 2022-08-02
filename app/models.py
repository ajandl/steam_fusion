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

    entries = db.relationship('List_entry', back_populates='user')

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

    steam_app_id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.Text, nullable=False)
    time_added = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    entries = db.relationship('List_entry', back_populates='app')


class List(db.Model):
    __tablename__ = 'lists'

    list_id = db.Column(db.Integer, primary_key=True, unique=True)
    list_name = db.Column(db.Text, nullable=False)
    creation_time = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    entries = db.relationship('List_entry', back_populates='list')


class List_entry(db.Model):
    __tablename__ = 'list_entries'

    # ForeignKey() takes an argument in the format table_name.column_name.
    # table_name and column_name come from the sql table, not the models.
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id'),
        primary_key=True,
    )
    app_id = db.Column(
        db.Integer,
        db.ForeignKey('steam_games.steam_app_id'),
        primary_key=True
    )
    list_id = db.Column(
        db.Integer,
        db.ForeignKey('lists.list_id'),
        primary_key=True
    )

    # relationship takes the first positional argument of Model_name,
    user = db.relationship('User', back_populates='entries')
    app = db.relationship('Steam_game', back_populates='entries')
    list = db.relationship('List', back_populates='entries')

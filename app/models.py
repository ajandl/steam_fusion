from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


"""
Using this structure for the database is inherently not efficient when trying
to get all the games that a user has on a list (such as their "owned" games).

To do something like this requires a query linking the users to list_roles and
then determining the list_id where they are an owner or have some other sort of
permission level set.  For other custom lists, another join to the lists table
is required to determine the list names and then the list_id.

Once the list_id is known, then the list_entries table can be queried.

This could result in many queries for a user who wants to see all of their
lists, but given the number of users we expect to have, this is acceptable.
"""


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

    entries = db.relationship('ListEntry', back_populates='user')
    roles = db.relationship('ListRoles', back_populates='user')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def set_steam(self, steamid='', steam_name=''):
        self.steamid = steamid
        self.steam_name = steam_name


class SteamGame(db.Model):
    __tablename__ = 'steam_games'

    steam_app_id = db.Column(db.Integer, primary_key=True, unique=True)
    game_title = db.Column(db.Text, nullable=False)
    time_added = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    entries = db.relationship('ListEntry', back_populates='app')


class ListsModel(db.Model):
    __tablename__ = 'lists'

    list_id = db.Column(db.Integer, primary_key=True, unique=True)
    list_name = db.Column(db.Text, nullable=False)
    list_creation_time = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    entries = db.relationship('ListEntry', back_populates='list_relationship')
    roles = db.relationship('ListRoles', back_populates='list_relationship')


class ListEntry(db.Model):
    __tablename__ = 'list_entries'

    # ForeignKey() takes an argument in the format table_name.column_name.
    # table_name and column_name come from the sql table, not the models.
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id'),
        primary_key=True,
    )
    steam_app_id = db.Column(
        db.Integer,
        db.ForeignKey('steam_games.steam_app_id'),
        primary_key=True
    )
    list_id = db.Column(
        db.Integer,
        db.ForeignKey('lists.list_id'),
        primary_key=True
    )
    time_entered = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # relationship takes the first positional argument of Model_name,
    user = db.relationship('User', back_populates='entries')
    app = db.relationship('SteamGame', back_populates='entries')
    list_relationship = db.relationship('ListsModel', back_populates='entries')


class ListRoles(db.Model):
    __tablename__ = 'list_roles'

    role_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    permission_lvl = db.Column(db.Text, nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.list_id'))
    role_set_time = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = db.relationship('User', back_populates='roles')
    list_relationship = db.relationship('ListsModel', back_populates='roles')

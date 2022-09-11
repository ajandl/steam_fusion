from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from app import db


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

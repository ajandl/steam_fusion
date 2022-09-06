from app import db
from datetime import datetime


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

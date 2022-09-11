from datetime import datetime
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

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    pw_hash = db.Column(db.Text, nullable=False)
    steam_id = db.Column(db.Text)
    steam_name = db.Column(db.Text)
    user_creation_time = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def set_steam(self, steam_id='', steam_name=''):
        self.steam_id = steam_id
        self.steam_name = steam_name

# TODO Add UserMixin, and login tracking
# TODO Create login endpoint
#   TODO Document endpoint
# TODO Create logout endpoint
#   TODO Document endpoint
# TODO Create user creation endpoint
#   TODO Document endpoint

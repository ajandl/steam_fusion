from werkzeug.security import generate_password_hash, check_password_hash


class UserMethods():

    @staticmethod
    def set_password(user, password):
        user.pw_hash = generate_password_hash(password)

    @staticmethod
    def check_password(user, password):
        return check_password_hash(user.pw_hash, password)

    def set_steam(user, steamid='', steam_name=''):
        user.steamid = steamid
        user.steam_name = steam_name

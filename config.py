import os
from datetime import timedelta


STEAM_API = os.environ.get('STEAM_API')


class Config():
    SECRECT_KEY = os.environ.get('SECRET_KEY') or 'secret-key-needs-change'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['jandl.wisc@gmail.com']
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'change_this_key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    STEAMID = os.environ.get('STEAMID')
    TOKEN_TIMEOUT = 30

import os

class Config(object):
    DEBUG = True
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    SECRET_KEY = os.environ['SECRET_KEY']
    FACEBOOK_APP_ID = os.environ['FACEBOOK_APP_ID']
    FACEBOOK_SECRET = os.environ['FACEBOOK_SECRET']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

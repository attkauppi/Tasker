""" Flask config """
# Based on tutorial from HackersAndSlackers.com
# https://hackersandslackers.com/configure-flask-applications/
import os
from os import environ, path
from dotenv import load_dotenv
from testing.postgresql import Postgresql

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))



class Config(object):
    """ Base config """
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    MAIL_DEBUG = True
    #SSL_REDIRECT = False
    # Static assets
    # TEMPLATES_FOLDER = 'templates'


class ProductionConfig(Config):
    print("Production config")
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    MAIL_DEBUG = True

class HerokuConfig(ProductionConfig):
    """ Production config for heroku """
    #SSL_REDIRECT = True if os.environ.get('DYNO') else False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    MAIL_DEBUG = True
    ADMINS=os.getenv('MAIL_USERNAME')

    @classmethod
    def init_app(cls, app):
        # Handle proxy server headers
        #from werkzeug.contrib.fixers import ProxyFix
        from werkzeug.middleware.proxy_fix import ProxyFix
        #app.wsgi_app = ProxyFix(app.wsgi_app)
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    DATABASE_URL = os.environ.get('DEV_DATABASE_URI')
    print("DATABASE_URL: ", DATABASE_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    print("debug mode: ", os.environ.get('DEBUG'))
    TESTING = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    MAIL_DEBUG = True
    ADMINS=os.getenv('MAIL_USERNAME')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')

class TestConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'default': DevConfig
}

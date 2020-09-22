""" Flask config """
# Based on tutorial from HackersAndSlackers.com
# https://hackersandslackers.com/configure-flask-applications/
import os
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config(object):
    """ Base config """
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.environ.get('PROD_DATABASE_URI')


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    # print("debug mode: ", os.environ.get('DEBUG'))
    TESTING = True
    DATABASE_URI = os.environ.get('DEV_DATABASE_URI')


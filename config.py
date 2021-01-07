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
    SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls, app):
        # Handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    DATABASE_URL = os.environ.get('DEV_DATABASE_URI')
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
    
#     import psycopg2
#     import testing.postgresql
#     from testing.postgresql import Postgresql
    
    
    # def handler(postgresql):
    #     conn = psycopg2.connect(**postgresql.dsn())
    #     cursor = conn.cursor()
    #     # cursor.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")

    #     # cursor.execute("CREATE TABLE messages(id SERIAL PRIMARY KEY, content TEXT, user_id INTEGER REFERENCES users, sent_at TIMESTAMP)")
    #     cursor.execute("CREATE TABLE messages(id SERIAL PRIMARY KEY, content TEXT)")
    #     cursor.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, email TEXT, created TIMESTAMP WITHOUT TIME ZONE, last_seen TIMESTAMP WITHOUT TIME ZONE)")
    #     cursor.execute("INSERT INTO messages (content) VALUES ('hello'), ('ciao')")
    #     cursor.execute("""CREATE TABLE tasks (
    #         id SERIAL PRIMARY KEY,
    #         creator_id INTEGER NOT NULL,
    #         title TEXT,
    #         description TEXT,
    #         created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    #         done BOOLEAN,
    #         FOREIGN KEY (creator_id) REFERENCES users (id)
    #     )""")
    #     cursor.close()
    #     conn.commit()
    #     conn.close()

    #Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True,
                                                  #on_initialized=handler)
#     postgresql = testing.postgresql.Postgresql()
#     DEBUG = True
#     TESTING = True
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SQLALCHEMY_DATABASE_URI = postgresql.url()
#     ENV = 'test'
#     TESTING = True


# config = {
#     'development': DevConfig,
#     'testing': TestConfig
# }

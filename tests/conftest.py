import psycopg2
import testing.postgresql
# from testing.postgresql import Postgresql
import os,sys,inspect
import pytest
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from application import create_app
from application import db as _db
# from application import app

# create initial data on create as fixtures into the database
def handler(postgresql):
    conn = psycopg2.connect(**postgresql.dsn())
    cursor = conn.cursor()
    # cursor.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")

    # cursor.execute("CREATE TABLE messages(id SERIAL PRIMARY KEY, content TEXT, user_id INTEGER REFERENCES users, sent_at TIMESTAMP)")
    cursor.execute("CREATE TABLE messages(id SERIAL PRIMARY KEY, content TEXT)")
    cursor.execute("INSERT INTO messages (content) VALUES ('hello'), ('ciao')")
    cursor.close()
    conn.commit()
    conn.close()

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True,
                                                  on_initialized=handler)

class TestConfig(object):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'test'
    TESTING = True

@pytest.yield_fixture(scope='session')
def app():
    _app = create_app()
    with Postgresql() as postgresql:
        _app.config['SQLALCHEMY_DATABASE_URI'] = postgresql.url()
        ctx = _app.app_context()
        ctx.push()

        yield _app

        ctx.pop()
    
@pytest.fixture(scope='session')
def testapp(app):
    return app.test_client()

@pytest.yield_fixture(scope='session')
def db(app):
    # _db.init_db()
    _db 
    _db.app = app
    _db.create_all()
    #_db.init_db()

    yield _db

    _db.drop_all()


@pytest.fixture(scope='function', autouse=False)
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)

    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()
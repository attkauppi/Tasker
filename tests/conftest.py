import psycopg2
import testing.postgresql
from testing.postgresql import Postgresql
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
    cursor.execute("""CREATE TABLE roles (
        id SERIAL PRIMARY KEY,
        role_name TEXT UNIQUE,
        default_role BOOLEAN,
        permissions INTEGER
    )""")
    cursor.execute("""CREATE TABLE team_roles (
    id SERIAL PRIMARY KEY,
    team_role_name TEXT,
    default_role BOOLEAN,
    team_permissions INTEGER
    )""")
    cursor.execute("""CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    CREATED TIMESTAMP WITHOUT TIME ZONE,
    MODIFIED TIMESTAMP WITHOUT TIME ZONE
    )""")
    cursor.execute("CREATE TABLE messages(id SERIAL PRIMARY KEY, content TEXT)")
    cursor.execute("""CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        about_me TEXT,
        confirmed BOOLEAN,
        created TIMESTAMP WITHOUT TIME ZONE,
        last_seen TIMESTAMP WITHOUT TIME ZONE,
        role_id INTEGER,
        avatar_hash TEXT,
        FOREIGN KEY (role_id) REFERENCES roles (id)
    )""")
    cursor.execute("""CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL,
    team_member_id INTEGER NOT NULL,
    team_role_id INTEGER NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams (id),
    FOREIGN KEY (team_member_id) REFERENCES users (id),
    FOREIGN KEY (team_role_id) REFERENCES team_roles (id)
    )""")
    cursor.execute("INSERT INTO messages (content) VALUES ('hello'), ('ciao')")
    cursor.execute("""CREATE TABLE tasks (
        id SERIAL PRIMARY KEY,
        creator_id INTEGER NOT NULL,
        title TEXT,
        description TEXT,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        position TEXT,
        done BOOLEAN,
        FOREIGN KEY (creator_id) REFERENCES users (id)
    )""")
    cursor.close()
    conn.commit()
    conn.close()

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True,
                                                  on_initialized=handler)

class TestConfig(object):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = Postgresql().url()
    ENV = 'test'
    TESTING = True
    ADMIN=os.getenv('ADMIN')

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
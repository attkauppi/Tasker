""" import unittest
import psycopg2
import testing.postgresql
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
from application.models import User, Task
from mock import patch
from application import create_app, db

# create initial data on create as fixtures into the database
def handler(postgresql):
    conn = psycopg2.connect(**postgresql.dsn())
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE messages(id SERIAL PRIMARY KEY, content TEXT)")
    cursor.execute("INSERT INTO messages (content) VALUES ('hello'), ('ciao')")
    cursor.close()
    conn.commit()
    conn.close()

# Use `handler()` on initialize database
Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True,
                                                  on_initialized=handler) 
                                                  
class UserModelCase(unittest.TestCase):                                                  

    def setUp(self):
        # Use the generated Postgresql class instead of testing.postgresql.Postgresql
        self.postgresql = Postgresql()
        self._app = create_app()
        self.app = self._app.test_client()
    
    def tearDown(self):
        self.postgresql.stop()
"""
import unittest
import psycopg2
import testing.postgresql
from flask import current_app
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
import testing.postgresql

from application import create_app, db
from application.models import User, Task, Permission, Role, AnonymousUser

# create initial data on create as fixtures into the database
def handler(postgresql):
    conn = psycopg2.connect(**postgresql.dsn())
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE messages(id SERIAL PRIMARY KEY, content TEXT)")
    cursor.execute("INSERT INTO messages (content) VALUES ('hello'), ('ciao')")
    cursor.close()
    conn.commit()
    conn.close()

# Use `handler()` on initialize database
Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True,
                                                  on_initialized=handler)

class TestConfig(object):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = Postgresql().url()
    ENV = 'test'
    TESTING = True

class UserModelCase(unittest.TestCase):
    def setUp(self):
        # Use the generated Postgresql class instead of testing.postgresql.Postgresql
        self.postgresql = Postgresql()
        print("postgresql url: ", self.postgresql.url())
        self._app = create_app()
        self._app.config['SQLALCHEMY_DATABASE_URI'] = self.postgresql.url()
        # self._app
        self.ctx = self._app.test_request_context()
        self.ctx.push()
        self.client = self._app.test_client()

        self.app = self._app.test_client()
        db.create_all()
        Role.insert_roles()
        
        # Yksi ohje taalta
        # https://stackoverflow.com/questions/16117094/flask-unit-tests-with-sqlalchemy-and-postgresql-exhausts-db-connections
    
    def tearDown(self):
        #self.postgresql.stop()
        db.session.remove()
        db.drop_all(app=self._app)
        print("db pool status")
        print(db.engine.pool.status())
        if self.ctx is not None:
            self.ctx.pop()
        self.postgresql.stop()


    # def setUp(self):
    #     # Use the generated Postgresql class instead of testing.postgresql.Postgresql
    #     self.postgresql = Postgresql()
    #     self._app = create_app()
    #     self.app = self._app.test_client()
    
    # def tearDown(self):
    #     self.postgresql.stop()
    
    def test_password_hashing(self):
        u = User(username="Testi")
        u.set_password("kissa")
        self.assertFalse(u.check_password("koira"))
        self.assertTrue(u.check_password("kissa"))

    def test_user_tasks_relationship(self):
        """ Tests that user's tasks can be found
        using the sqlalchemy relationship. """
        u = User(username="Testi", email="Testi@Testi.com")
        u.set_password("Kissa")
        db.session.add(u)
        #print("u.id: ", u.id)
        db.session.commit()
        t = Task(title="tTehtävä", description="Tehtävä kuvaus", creator_id=u.id)
        db.session.add(t)
        db.session.commit()
        self.assertIn(t, u.tasks)
        l = u.tasks.copy()
        tehtava = l.pop()
        self.assertEqual(tehtava.title, "tTehtävä")

    # @patch('models.user.verify_reset_password_token', lambda x:x)
    # def test_token_generation_verification(self):
    #     u = User(username="Testi")
    #     u.set_password=("kissa")
    #     u.email = "testi@localhost.com"
    #     db.session.add(u)
    #     self.app.post('/')
    #     # db.session.add(u)
    #     print(u.get_reset_password_token())
    #     self.assertEqual(u.verity_reset_password_token(u.get_reset_password_token()), u.id)
    def test_user_role(self):
        """ Tests that a basic user can only create tasks and create groups """
        u = User(username='john', email='john@exampleexample.com', password='cat')
        self.assertTrue(u.can(Permission.CREATE_TASKS))
        self.assertTrue(u.can(Permission.CREATE_GROUPS))
        self.assertFalse(u.can(Permission.CREATE_GROUP_TASKS))
        self.assertFalse(u.can(Permission.MODERATE_GROUP))
        self.assertFalse(u.can(Permission.ADMIN))
    
    def test_anynymous_user(self):
        """ Anonymous user should not be allowed to do
        any of these functions/tasks """
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.CREATE_TASKS))
        self.assertFalse(u.can(Permission.CREATE_GROUPS))
        self.assertFalse(u.can(Permission.CREATE_GROUP_TASKS))
        self.assertFalse(u.can(Permission.MODERATE_GROUP))
        self.assertFalse(u.can(Permission.ADMIN))
    



if __name__ == '__main__':
    unittest.main(verbosity=3)

    
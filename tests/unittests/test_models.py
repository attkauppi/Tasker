import unittest
import psycopg2
import testing.postgresql
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
from application.models import User
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
    
    def test_password_hashing(self):
        u = User(username="Testi")
        u.set_password("kissa")
        self.assertFalse(u.check_password("koira"))
        self.assertTrue(u.check_password("kissa"))
    
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


if __name__ == '__main__':
    unittest.main(verbosity=2) 

    
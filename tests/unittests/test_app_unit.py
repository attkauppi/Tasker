import unittest
import psycopg2
import testing.postgresql
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)

from application import create_app

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

class TestAppUnit(unittest.TestCase):
    def setUp(self):
        # Use the generated Postgresql class instead of testing.postgresql.Postgresql
        self.postgresql = Postgresql()
        self._app = create_app()
        self.app = self._app.test_client()
    
    def tearDown(self):
        self.postgresql.stop()

    def test_home_page(self):
        response = self.app.get("/")
        print("response: ", response.status_code)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"viesti" in response.data)

if __name__ == '__main__':
    unittest.main()
    

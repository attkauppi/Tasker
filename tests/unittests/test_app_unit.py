from unittest import TestCase
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

#from flask_webtest import TestApp
from application import create_app, db
from application.models import User,Task

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
    WTF_CSRF_ENABLED = False

class TestAppUnit(unittest.TestCase):
    def setUp(self):
        # Use the generated Postgresql class instead of testing.postgresql.Postgresql
        self.postgresql = Postgresql()
        #print("postgresql url: ", self.postgresql.url())
        self._app = create_app()
        self._app.config['SQLALCHEMY_DATABASE_URI'] = self.postgresql.url()
        # self._app
        self.ctx = self._app.test_request_context()
        self.ctx.push()
        self.client = self._app.test_client()

        self.app = self._app.test_client()
        db.create_all()
        
        # Yksi ohje taalta
        # https://stackoverflow.com/questions/16117094/flask-unit-tests-with-sqlalchemy-and-postgresql-exhausts-db-connections
    
    def tearDown(self):
        #self.postgresql.stop()
        db.session.remove()
        db.drop_all(app=self._app)
        #print("db pool status")
        #print(db.engine.pool.status())
        if self.ctx is not None:
            self.ctx.pop()
        self.postgresql.stop()

    def test_home_page(self):
        response = self.app.get("/")
        #print("response: ", response.status_code)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"viesti" in response.data)
        
    def test_register_page(self):
        """ Tests whether register page is reachable """
        response = self.app.get("/auth/register")
        #print("Register statuscode: ", response.status_code)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"Username" in response.data)
        self.assertTrue(b"Email" in response.data)
        self.assertTrue(b"Password" in response.data)
        self.assertTrue(b"Repeat password" in response.data)        

    def test_valid_registration(self):
        response = self.register(
            'testi',
            'testi@localhost.com',
            'testiS',
            'testiS'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        """ Tests if login page is reachable and
        whether certain default content can be found
        on it. """
        response = self.app.get("/auth/login")
        # print("login status.code: ", response.status_code)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"login" in response.data)
        self.assertTrue(b"username" in response.data)
        self.assertTrue(b"password" in response.data)
        self.assertTrue(b"New user?" in response.data)
    
    def test_log_in(self):
        """ Tests logging in """
        u = User()
        u.username = "ttesti"
        u.set_password("ttestiS")
        #u.set_password("ttestiS")
        db.session.add(u)
        db.session.commit()
        response = self.login('ttesti', 'ttestiS')
        self.assertEqual(response.status_code, 200)
    
    def test_access_user_page_without_login(self):
        """ 
        Tests whether it's possible to access the /user/<username> path
        without logging in -- it shouldn't be.
        """
        # To test, we need a user that could
        # theoretically have a user page
        response = self.register(
            'testi',
            'testi@localhost.com',
            'testiS',
            'testiS'
        )
        response = self.app.get("/user/testi")
        print("resp status code: ", response.status_code)
        self.assertFalse(b"Task title" in response.data)
        # Should be 302, when attempted access without logon; redirects to login page.
        self.assertTrue(response.status_code, 302)
    
    # def test_profile_page(self):
    #     """ Tets whether profile page is accessible """
    #     u = User()
    #     u.username = "ttesti"
    #     u.set_password("ttestiS")
    #     u.confirmed = True
    #     #u.set_password("ttestiS")
    #     db.session.add(u)
    #     db.session.commit()

    #     response = self.app.post(
    #         "/auth/login",
    #         data=dict(
    #             username=u.username,
    #             password=u.password,
    #         ),
    #         follow_redirects=True
    #     )

    #     print("Response: ", response)

        
        
    #     response = self.app.get('/user/ttesti')
    #     print("RESPONSE.DATA: ", response.data)
    #     print("RESPONSE STATUS CODE: ", response.status_code)
        
    #     self.assertIn(b"Belongs to teams", response.data)


        







    # def test_add_task(self):
    #     """ Tests adding a task """
    #     #self.register(
    #     #    'testi',
    #     #    'testi@localhost.com',
    #     #    'testiS',
    #     #    'testiS'
    #     #)
    #     #self.login('ttesti', 'ttestiS')
    #     u = User()
    #     u.username = "ttesti"
    #     u.email = "ttesti@ttestaaja.com"
    #     u.set_password("ttestiS")
        
    #     db.session.add(u)
    #     db.session.commit()
    #     response = self.login('ttesti', 'ttestiS')

    #     # data=dict(
    #     #         username=u.username,
    #     #         password=u.password
    #     #     )

    #     # with self.client as client:
    #     #     #client.preserve_context
    #     #     res = client.post('/auth/login', data=data, follow_redirects=True)
    #     #     res = client.get('/user/ttesti', follow_redirects=True)
            
    #     #     print("uuden kokeilun status_code: ", res.status_code)
    #     #     print(res.data.decode())
    #     u = "testi"
    #     p = "testip"
    #     p2 = "testip"
    #     email = "testi@testi.fi"

    #     r = self.register(u, email, p, p2)
    #     self.assertTrue(r.status_code, 200)

    #     r = self.login(u, p)
    #     self.assertTrue(r.status_code, 200)

    #     r = self.client.get('/user/testi', follow_redirects=True)

    #     #response = self.login(u.username, u.password)
    #     #print(response.get_data(as_text=True))
    #     print(r.get_data(as_text=True))
    #     self.assertTrue(b"Hei ttesti" in r.data)

        #self.app.login_manager.init_app(app)
        #self.client = webtest.TestApp(app)
        #self.login('ttesti', 'ttestiS')
        #self.app.post('/login')
        # self.app.post(
        #     '/auth/login',
        #     data=dict(
        #         username=u.username,
        #         password=u.password
        #     ),
        #     follow_redirects=True
        # )

        #response = self.app.get('/user/testi')
        
        #response = self.app.get('/user/testi')
        #self.assertEqual(500, 200)
        #response = self.app.get('/user/testi')

        




    ############################
    #### Helper methods ########
    ############################
    # Vinkki taalta: https://www.patricksoftwareblog.com/unit-testing-a-flask-application/
    def register(self, username, email, password, password2):
        """ Registers created user """
        return self.app.post(
            "/auth/register",
            data=dict(
                username=username,
                password=email,
                password2=password,
                email=email
            ),
            follow_redirects=True
        )
    
    def login(self, username, password):
        """ Helper method for logging in """
        return self.app.post(
            '/auth/login',
            data=dict(
                username=username,
                password=password
            ),
            follow_redirects=True
        )

if __name__ == '__main__':
    unittest.main()
    

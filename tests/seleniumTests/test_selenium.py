from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import os,sys,inspect
#import pytest
#currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#parentdir = os.path.dirname(currentdir)

import unittest
import time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
from application import create_app, db
from application.models import User, Team, Role, Permission, TeamPermission, TeamRole, Task
from application import faker
import re
import threading


import unittest
import psycopg2
import testing.postgresql
from flask import current_app
import os,sys,inspect
import time

import testing.postgresql

from application import create_app, db
from application.models import User, Task, Permission, Role, AnonymousUser, Team, TeamMember, TeamPermission, TeamRole

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

class SeleniumTestCase(unittest.TestCase):
    """ Class for testing with selenium 
    
    To use this class, please place a chromedriver
    in the same folder as this file. """

    client = None
    #client = webdriver.Chrome(currentdir+"/chromedriver")
    #client.get('http://www.google.com/'); time.sleep(10)

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()

        #cls.client = webdriver.Chrome(currentdir+"/chromedriver")
        
        
        try:
            #cls.client = webdriver.Chrome(chrome_options=options)
            print("CURRENT DIR: ", currentdir)
            cls.client = webdriver.Chrome(currentdir+"/chromedriver"); time.sleep(10)
            #cls.client.get('google.com'); time.sleep(10)
        except:
            pass
    
        # Skip if browser can't be started
        if cls.client:
            print("Iffin sisällä")

            # Oma lisäys
            cls.postgresql = Postgresql()
            print("postgresql url: ", cls.postgresql.url())
            # Create the flask application
            cls.app = create_app('config.TestConfig')
            cls.app.config['TESTING'] = True
            cls.app.config['SQLALCHEMY_DATABASE_URI'] = cls.postgresql.url()

            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # Create the database
            db.create_all()
            Role.insert_roles()
            TeamRole.insert_roles()

            u = User(
                username="testaaja25",
                email="testaa25@localhost.com",
                confirmed=True
            )
            u.set_password('testaaja25')

            db.session.add(u)
            db.session.commit()
            
            faker.users(10)

            cls.server_thread = threading.Thread(
                target=cls.app.run,
                kwargs={'debug':False}
            )

            cls.server_thread.start()
            time.sleep(10)

            # add an administrator user
            # admin_role = Role.query.filter_by(name='Administrator').first()
            # admin = User(email='john@example.com',
            #              username='john', password='cat',
            #              role=admin_role, confirmed=True)
            # db.session.add(admin)
            # db.session.commit()


            # Create database and populate with some fake data
            
            #webdriver.Chrome(currentdir+"/chromedriver")
            #driver.get("google.com")
        print("Lopussa")
    
    
    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the flask server and the browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            # destroy database
            db.drop_all()
            db.session.remove()

            # remove application context
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')
    
    def tearDown(self):
        pass

    
    def test_home_page(self):
        self.client.get('http://localhost:5000/')
        time.sleep(3)
        tasker = self.client.find_element_by_xpath("/html/body/nav/div[1]/a").text
        self.assertEqual(tasker, "Tasker")

        self.client.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]').click()
        time.sleep(5)
    
    def test_login(self):
        """ Test logging in """
        self.client.get('http://127.0.0.1:5000/auth/login')
        time.sleep(3)

        # Finds the login button from the navbar and clicks
        self.client.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]').click()
        time.sleep(3)

        # Finds username field
        username= self.client.find_element_by_id('username')
        username.send_keys('testaaja25')
        time.sleep(2)

        # finds password field
        password = self.client.find_element_by_id('password')
        password.send_keys('testaaja25')

        time.sleep(2)

        # submit button
        self.client.find_element_by_id('submit').click()
        time.sleep(10)

        self.assertIn("<h1>Hei testaaja25</h1>", self.client.page_source)
        
if __name__ == '__main__':
    unittest.main()



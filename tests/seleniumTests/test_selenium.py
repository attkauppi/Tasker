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
            cls.client = webdriver.Chrome(currentdir+"/chromedriver")
            cls.client.implicitly_wait(10)
            #cls.client.get('google.com'); time.sleep(10)
        except:
            pass
    
        # Skip if browser can't be started
        if cls.client:
            print("Iffin sisällä")
            #cls.client.implicitly_wait(30)
            #cls.client.maximize_window()

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
                kwargs={
                    'debug':'false',
                    'use_reloader': False,
                    'use_debugger': False
                }
            )

            cls.server_thread.start()
            #time.sleep(10)

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
        # time.sleep(3)
        tasker = self.client.find_element_by_xpath("/html/body/nav/div[1]/a").text
        self.assertEqual(tasker, "Tasker")

        #self.client.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]').click()
        #time.sleep(5)
    
    def test_login(self):
        """ Test logging in """
        self.client.get('http://localhost:5000/auth/login')
        # time.sleep(3)

        # Finds the login button from the navbar and clicks
        #self.client.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]').click()
        #self.client.find_element_by_link_text('Log In').click()
        
        time.sleep(3)

        # Finds username field
        try:
            username= self.client.find_element_by_id('username').click()
            time.sleep()
            username.send_keys('testaaja25')
            #time.sleep(2)
        except Exception:
            pass

        # finds password field
        try:
            password = self.client.find_element_by_id('password').click()
            time.sleep(2)
            password.send_keys('testaaja25')
            time.sleep(2)
        except Exception:
            pass

        
        # time.sleep(2)

        # submit button
        try:
            self.client.find_element_by_id('submit').click()
            time.sleep(2)
            # time.sleep(10)
        except Exception:
            pass

        self.assertIn("<h1>Hei testaaja25</h1>", self.client.page_source)
    
    def test_create_team(self):
        """ Tests that creating a team is possible """
        
        # Log in ######
        try:
            self.client.get('http://localhost:5000/auth/login')
            time.sleep(3)

            # Finds the login button from the navbar and clicks
            #self.client.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]').click()
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
            time.sleep(5)
            #######

            # Finds the create team button
            self.client.find_element_by_id('team').click()
            time.sleep(2)
            self.client.find_element_by_link_text('Create team').click()
            time.sleep(3)
            
            #time.sleep(3)

            # Finds the team name field
            team_title = self.client.find_element_by_id('title')
            team_title.send_keys('testaaja25:sen tiimi')
            #time.sleep(3)

            # Finds the description field
            team_desc = self.client.find_element_by_id('description')
            team_desc.send_keys('description')
            #time.sleep(3)
            print("TIIMIN LUONTI TESTI")

            # Finds the submit button
            self.client.find_element_by_id('submit').click()
            # time.sleep(5)
            print("Submittasko?")

            #time.sleep(3)
        except Exception:
            pass

        self.assertIn('testaaja25:sen tiimi', self.client.page_source)
        self.assertIn('Team members', self.client.page_source)
    
    def test_tasks(self):
        """ Tests task functionalities """
        #text = None
        try:

            #t = Team('')

            # Create team
            print("Team tasks alkaa")
            # time.sleep(2)
            # self.client.get('http://localhost:5000/auth/login')
            # time.sleep(3)

            # # Finds the login button from the navbar and clicks
            # #self.client.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]').click()
            # #time.sleep(3)

            # # Finds username field
            # username= self.client.find_element_by_id('username')
            # username.send_keys('testaaja25')
            # time.sleep(2)

            # # finds password field
            # password = self.client.find_element_by_id('password')
            # password.send_keys('testaaja25')

            # time.sleep(2)

            # # submit button
            # self.client.find_element_by_id('submit').click()
            # time.sleep(5)
            # #######

            # # Finds the create team button
            # self.client.find_element_by_id('team').click()
            # time.sleep(2)
            # self.client.find_element_by_link_text('Create team').click()
            # time.sleep(3)
            
            # #time.sleep(3)

            # # Finds the team name field
            # team_title = self.client.find_element_by_id('title')
            # team_title.send_keys('testaaja25:sen tiimi')
            # #time.sleep(3)

            # # Finds the description field
            # team_desc = self.client.find_element_by_id('description')
            # team_desc.send_keys('description')
            # #time.sleep(3)
            # print("TIIMIN LUONTI TESTI")

            # # Finds the submit button
            # self.client.find_element_by_id('submit').click()
            # time.sleep(5)
            # print("Submittasko?")
            #################

            # self.client.get('http://localhost:5000/auth/login')
            # time.sleep(3)

            # # Finds the login button from the navbar and clicks
            # #self.client.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]').click()
            # #time.sleep(3)

            # # Finds username field
            # username= self.client.find_element_by_id('username')
            # username.send_keys('testaaja25')
            # time.sleep(2)

            # # finds password field
            # password = self.client.find_element_by_id('password')
            # password.send_keys('testaaja25')

            # time.sleep(2)

            # # submit button
            # self.client.find_element_by_id('submit').click()
            # time.sleep(5)
            #######

            self.client.get('http://localhost:5000/team/1')
            time.sleep(3)

            print("Get team tasks page")
            self.client.get('http://localhost:5000/teams/1/team_tasks')
            time.sleep(3)

            # Click Team tasks2 on navbar
            self.client.find_element_by_xpath('/html/body/div[1]/div/div[2]/ul[1]/li[3]').click()
            time.sleep(4)

            # Create task
            self.client.find_element_by_xpath('/html/body/div[2]/p[3]/button').click()
            title = self.client.find_element_by_id('title')
            title.send_keys('otsikko')
            time.sleep(4)

            desc = self.client.find_element_by_id('description')
            desc.send_keys('kuvaus')
            time.sleep(5)

            # Create button
            self.client.find_element_by_id('submit_new_task').click()
            time.sleep(5)

            # Move right
            self.client.find_element_by_xpath('//*[@id="task_span"]/div/div[2]/table/tbody/tr/td[4]/form/button').click()
            time.sleep(5)
            
            
            # test
            # moved_right = "Moved right" in self.client.page_source

            # Move left
            self.client.find_element_by_xpath('/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/table/tbody/tr/td[1]/form/button').click()
            time.sleep(4)
            #moved_left = "Moved left" in self.client.page_source

            time.sleep(3)


            # Edit
            #self.find_element_by_xpath('//*[@id="task_span"]/div/div[2]/table/tbody/tr/td[2]/a').click()
            #
            self.client.find_element_by_id('edit').click()
            # self.find_element_by_xpath('//*[@id="task_span"]/div/div[2]/table/tbody/tr/td[2]/a').click()
            # print("Clidk edit")
            time.sleep(5)
            # self.find_element_by_css_selector('a.edit-modal-opener34').click()
            # //*[@id="task_span"]/div/div[2]/table/tbody/tr/td[2]/a/span

            title = self.client.find_element_by_id('title')
            title.send_keys('otsikko muokattu')

            time.sleep(4)

            # Assign to
            self.client.find_element_by_xpath('//*[@id="assign_to_choices"]').click()
            time.sleep(3)
            self.find_element_by_xpath('//*[@id="assign_to_choices"]/option[2]').click()
            time.sleep(2)

            # move to
            self.client.find_element_by_xpath('//*[@id="board_choices"]').click() 
            time.sleep(5)
            self.client.find_element_by_xpath('//*[@id="board_choices"]/option[2]').click()
            time.sleep(2)

            # submit
            self.client.find_element_by_id('submit_edit_team_task').click()

            text = self.client.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/div[2]/div[1]').text
            self.assertTrue("otsikko muokattu" in text)

            time.sleep(3)

        except Exception:
            pass

        # Otsikko teksti sivulla haettuna xpathin mukaan 
        #text = self.client.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/div[2]/div[1]').text
        #self.assertTrue("otsikko muokattu" in text)
        self.assertTrue('assigned to' in self.client.page_source)
        self.assertTrue('testaaja25' in self.client.page_source)

    def test_invite_to_team(self):
        """ Tests inviting """

        try:
            self.client.get('http://127.0.0.1:5000/teams/1/invites')
            time.sleep(3)
            
                    
        except Exception:
            pass


    # def test_creator_is_team_owner(self):
    #     """ Tests that the creator of the team
    #     becomes its owner """
    #     try:
    #         print("IS OWNER")
    #         self.client = self.login()

    #         time.sleep(2)
    #         self.client.get('http://localhost:5000/user/testaaja25')
    #         time.sleep(2)

    #         self.client.find_element_by_xpath('/html/body/div[1]/table/tbody/tr/td[3]/ul/li[1]/a').click()
    #         time.sleep(2)
    #         #self.client.find_element_by_partial_link_text('')


    #         #self.client.find_element_by_id('team').click()
    #         #time.sleep(2)
    #         print("Current url: ", self.client.current_url)
    #         self.client.find_element_by_link_text('Members').click()
    #         time.sleep(10)

    #         self.client.find_element_by_link_text('testaaja25:sen tiimi').click()
    #         time.sleep(3)

    #     except Exception:
    #         pass

    #     self.assertIn('Team owner', self.client.page_source)
    
    # def test_can_invite_to_team(self):
    #     """ Tests that it's possible to invite users to team """
    #     try:
    #         self.client = self.login()

    #         time.sleep(2)
    #         self.client.get('http://localhost:5000/user/testaaja25')
    #         time.sleep(2)

    #         self.client.find_element_by_xpath('/html/body/div[1]/table/tbody/tr/td[3]/ul/li[1]/a').click()
    #         time.sleep(2)
    #         print("Current url: ", self.client.current_url)
    #         self.client.find_element_by_link_text('Members').click()
    #         time.sleep(10)

    #         self.client.find_element_by_link_text('testaaja25:sen tiimi').click()
    #         time.sleep(3)

    #         self.client.find_element_by_id('invite_to_team').click()
    #         self.client.sleep(10)
    #     except Exception:
    #         pass

    ########### UTILITY METHODS ######
    def login(self):
        print("LOGIN")
        try:
            self.client.get('http://127.0.0.1:5000/auth/login')
            time.sleep(3)

            # Finds the login button from the navbar and clicks
            #self.client.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]').click()
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
            time.sleep(5)
        except Exception:
            pass
        return self.client
    
    def create_team(self):
        try:
            self.client.get('http://localhost:5000/auth/login')
            time.sleep(3)

            # Finds the login button from the navbar and clicks
            #self.client.find_element_by_xpath('//*[@id="bs-example-navbar-collapse-1"]/ul[4]').click()
            #time.sleep(3)

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
            time.sleep(5)
            #######

            # Finds the create team button
            self.client.find_element_by_id('team').click()
            time.sleep(2)
            self.client.find_element_by_link_text('Create team').click()
            time.sleep(3)
            
            #time.sleep(3)

            # Finds the team name field
            team_title = self.client.find_element_by_id('title')
            team_title.send_keys('testaaja25:sen tiimi')
            #time.sleep(3)

            # Finds the description field
            team_desc = self.client.find_element_by_id('description')
            team_desc.send_keys('description')
            #time.sleep(3)

            # Finds the submit button
            self.client.find_element_by_id('submit').click()

            #time.sleep(3)
        except Exception:
            pass
            
        return self.client


        
if __name__ == '__main__':
    unittest.main()



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
import time
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
import testing.postgresql

from application import create_app, db
from application.models import User, Task, Permission, Role, AnonymousUser, Team, TeamMember, TeamPermission, TeamRole, Message, Notification, TeamTask

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
        self._app.config['TESTING'] = True
        #self._app.update_config
        self._app.config['SQLALCHEMY_DATABASE_URI'] = self.postgresql.url()
        # self._app
        self.ctx = self._app.test_request_context()
        self.ctx.push()
        self.client = self._app.test_client()

        self.app = self._app.test_client()
        db.create_all()
        Role.insert_roles()
        TeamRole.insert_roles()
        
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

    def test_administrator_role(self):
        """ Administrator should be allowed to do all tasks """
        r = Role.query.filter_by(role_name='Administrator').first()
        u = User(email='tasker.info.noreply@gmail.com', password='kissa', role=r)
        self.assertTrue(u.can(Permission.ADMIN))
        self.assertTrue(u.can(Permission.CREATE_GROUPS))
        self.assertTrue(u.can(Permission.CREATE_GROUP_TASKS))
        self.assertTrue(u.can(Permission.CREATE_TASKS))
        self.assertTrue(u.can(Permission.MODERATE_GROUP))
    
    def test_group_moderator_role(self):
        """" A group moderator is allowed to moderate groups, but not
        administer the site """
        r = Role.query.filter_by(role_name='Moderator').first()
        u = User(email='esimerkki@esimerkki.com', password='kissa', role=r)
        self.assertFalse(u.can(Permission.ADMIN))
        self.assertTrue(u.can(Permission.CREATE_GROUPS))
        self.assertTrue(u.can(Permission.CREATE_GROUP_TASKS))
        self.assertTrue(u.can(Permission.CREATE_TASKS))
        self.assertTrue(u.can(Permission.MODERATE_GROUP))
    
    def test_group_member_role(self):
        """ A group member is allowed to create tasks etc. in groups,'
        but not moderate them nor administer the site """
        r = Role.query.filter_by(role_name='Group role').first()
        u = User(email='esimerkki@esimerkki.com', password='kissa', role=r)
        self.assertTrue(u.can(Permission.CREATE_TASKS))
        self.assertTrue(u.can(Permission.CREATE_GROUPS))
        self.assertTrue(u.can(Permission.CREATE_GROUP_TASKS))
        self.assertFalse(u.can(Permission.MODERATE_GROUP))
        self.assertFalse(u.can(Permission.ADMIN))
    
    # Token tests
    def test_valid_confirmation_token(self):
        """ Tests whether confirmation sent to newly
        registered user is valid 
        
        This test should pass, because it tests the token
        against the user itself (actually it checks that the
        id is the the same one as the user's id.) """
        u = User(username='u', password='correct')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        """ Tests that confirmation tokens fail, when
        the wrong user is given another user's token """
        u1 = User(username='u1', password='c')
        u2 = User(username='u2', password='d')
        db.session.add(u1, u2)
        db.session.commit()

        u1_token = u1.generate_confirmation_token()
        u2_token = u2.generate_confirmation_token()
        self.assertFalse(u2.confirm(u1_token))
        self.assertFalse(u1.confirm(u2_token))
        self.assertFalse(u1.confirm(None))
    
    def test_expired_confirmation_token(self):
        """ Tests that confirmation tokens fail,
        when out of date. """
        u1 = User(username='u1', password='u1')
        db.session.add(u1)
        db.session.commit()

        # Creates a confirmation token with expiration
        # time of 1 second.
        token = u1.generate_confirmation_token(1)

        # Wait for 2 seconds to ensure token will be
        # expired
        time.sleep(2)
        self.assertFalse(u1.confirm(token))
    
    def test_user_team_memberships(self):
        """ Test that user can use the relationship
        between user and teams """
        u = User(username='u1', password='u1')
        db.session.add(u)
        db.session.commit()
        u = User.query.filter_by(username=u.username).first()


        t = Team(title='u1sen tiimi', description='Tämä on testi tiimi')
        db.session.add(t)
        db.session.commit()

        t = Team.query.filter_by(title=t.title).first()

        # 5 = admin
        tr = TeamRole.query.filter_by(id=4).first()
        print("Team role: ", tr)

        # Create team member
        tm = TeamMember(
            team_id = t.id,
            team_member_id = u.id,
            team_role_id = tr.id
        )

        print("TeamMember olio kun luotu: ", tm)

        

        db.session.add(tm)
        db.session.commit()

        tm2 = TeamMember.query.filter_by(team_member_id=tm.team_member_id).first()

        print("Käyttäjän tiimiläisolio: ", u.get_team_member_object(t.id))

        print("Ennen testiä, haettu tietokannasta: ", tm2)
        self.assertFalse(u.is_team_administrator(t.id))
        # Checks that Admins have Moderator rights as well
        self.assertTrue(u.is_team_moderator(t.id))
        # Checks that the actual role the user has is Administrator
        self.assertFalse(u.is_team_role(t.id, "Administrator"))
        # Checks that the user's actual role isn't Moderator despite
        # the user having moderator rights as administrator
        self.assertTrue(u.is_team_role(t.id, "Team owner"))
        self.assertFalse(u.is_team_role(t.id, "Team moderator"))
        self.assertTrue(u.can_team(t.id, TeamPermission.MODERATE_TEAM))

        team_role_u = u.get_team_role(t.id)
        self.assertTrue(team_role_u.has_permission(TeamPermission.MODERATE_TEAM))




    



if __name__ == '__main__':
    unittest.main(verbosity=3)

    
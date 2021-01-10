from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from application import db
from application.models import User, Team, TeamMember, TeamRole, Task, Permission
list_of_fake_users = []

def users(count=10):
    """ Generates fake users for testing """
    fake = Faker()
    i = 0

    while i < count:
        u = User(
            email=fake.email(),
            username = fake.user_name(),
            password='password',
            confirmed=True
        )
        print("Fake user: ", u)
        print("fake user email: ", u.email)

        db.session.add(u)
        list_of_fake_users.append(u)
        
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def get_fake_users():
    return list_of_fake_users
# def teams(count=10):
#     fake = Faker()



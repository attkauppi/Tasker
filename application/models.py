# from . import db
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from application import db, login_manager
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text, Boolean)
from datetime import date
from datetime import datetime
from time import time
import jwt
import os
import hashlib
from urllib import request

class User(UserMixin, db.Model):
    """ User accont db model """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=True)
    about_me = db.Column(db.Text(), nullable=True)
    created = db.Column(DateTime, default=datetime.utcnow())
    last_seen = db.Column(DateTime, default=datetime.utcnow())
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    avatar_hash = db.Column(db.String(32))
    #tasks = db.relationship('Task', backref='author', lazy=True)
    tasks = relationship("Task", back_populates='user')
    teams = relationship("Team", secondary="team_members")
    # tasks = db.relationship('Task', back_populates='users')
    #tasks = db.relationship('Task', backref='user', lazy='dynamic')

    # Turha kommentti


    def __init__(self, **kwargs): # Initializes user roles
        """ Sets user roles. Sets Admin if email matches """
        super(User, self).__init__(**kwargs)
        #self.email = email
        # self.username = username
        # self.password = password
        print(self.role)
        if self.role is None:
            print("self email: ", self.email)
            print("os.getenv(admin): ", os.getenv('ADMIN'))
            #if self.email == os.getenv('ADMIN'):
            # This will not work, if in the registration form
            # the user is not instantiated with at least the
            # email, i.e., u = User(email=form.email.data)
            if self.email == os.getenv('ADMIN'): # Checks whether the email address of the user matches that of the admin's
                # TODO: Tietokantaviritykset lopuksi
                print("Ei päässyt iffiin")
                self.role = Role.query.filter_by(role_name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default_role=True).first()
        # Gravatar
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        """ Sets user password, hashed """
        print("generate_password_hash: ", generate_password_hash(password))
        self.password = generate_password_hash(password)

    def check_password(self, password):
        print("Checking password: ")
        print("self.password: ", password)
        generated_password = generate_password_hash(password)
        print("Generated", generated_password)
        print("self.pass", self.password)
        
        if self.password == generated_password:
            print("Olivat mukamas samat")

        return check_password_hash(self.password, password)
    
    def get_reset_password_token(self, expires_in=3600):
        """ Sends a user a password reset token in email """
        print("self: ", self)
        print("self.id: ", str(self.id))
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')
    
    @staticmethod
    def verity_reset_password_token(token):
        """ Verifies a password token generated for user """
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256']
            )['reset_password']
        except:
            return
        return User.query.get(id)
    
    # User role check
    def can(self, perm):
        """ Retruns true if the requested permission is present
        in the role. """
        return self.role is not None and self.role.has_permission(perm)
    
    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def gravatar_hash(self):
        """ Gravatar method will use the stored hash, if available
        If not, this method will recalculate the gravatar hash """
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        """ Fetches an avatar given a person's user account using
        the gravatar.com service, which turns a person's email address
        into a profile picture, if they've registered to gravatar.com """
        #if request.is_secure:
        url = 'https://secure.gravatar.com/avatar'
        #else:
        #    url = 'http://gravatar.com/avatar'
        # An email address is turned into an md5 hash on gravatar
        # so the url is https://secure.gravatar.com/avatar/[email address hashed with md5]
        # hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,
            hash=hash,
            size=size,
            default=default,
            rating=rating
        )

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

class Role(db.Model):
    """ Implements roles for users """
    #TODO: Lisää roolit schema.sql:n
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64), unique=True)
    default_role = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(Integer)
    users = relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
    
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permissions(self, perm):
        if self.has_permissions(perm):
            self.permissions -= perm
    
    def reset_permissions(self):
        self.permissions = 0
    
    def has_permission(self, perm):
        return self.permissions & perm == perm
    
    def __repr__(self):
        return '<Role %r>' % self.role_name
    
    @staticmethod
    def insert_roles():
        # TODO: On lisättävä email confirmation, jotta admin-tiliä ei voida kaapata.
        """
        Tries to find existing roles by name and update
        those. A new role is created only for those roles
        that aren't in the database already. This is done
        so the role list can be updated in the future when
        changes need to be made.

        This gives admission priveleges to the user who has
        the admin email address (defined in .env in the root
        folder). Whoever has this address, is the admin user.
        ==> Would work better, if confirmation emails would be
        possible to send.
        """
        roles = {
            'User': [Permission.CREATE_TASKS, Permission.CREATE_GROUPS],
            'Group role': [Permission.CREATE_TASKS,
                Permission.CREATE_GROUPS, 
                Permission.CREATE_GROUP_TASKS],
            'Moderator': [Permission.CREATE_TASKS,
                Permission.CREATE_GROUPS,
                Permission.CREATE_GROUP_TASKS,
                Permission.MODERATE_GROUP],
            'Administrator': [Permission.CREATE_TASKS,
                Permission.CREATE_GROUPS,
                Permission.CREATE_GROUP_TASKS,
                Permission.MODERATE_GROUP,
                Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(role_name=r).first()
            if role is None:
                role = Role(role_name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default_role = (role.role_name == default_role)
            db.session.add(role)
        db.session.commit()

class Permission:
    CREATE_TASKS = 1
    CREATE_GROUPS = 2
    CREATE_GROUP_TASKS = 4
    MODERATE_GROUP = 8
    ADMIN = 16

class Messages(db.Model):
    """ A Model of messages table """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    def __repr__(self):
        return f"Message saved: {self.message}"

class Task(db.Model):
    """ A model of tasks """
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text())
    description = db.Column(db.Text())
    created = db.Column(DateTime, default=datetime.utcnow())
    done = db.Column(db.Boolean)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    #user = db.relationship('User')
    user = relationship('User', back_populates='tasks')
    #user = db.relationship('User', innerjoin=True, back_populates='tasks')

    def __repr__(self):
        return "<Task {}>".format(self.title)

class Team(db.Model):
    """ A team data model """
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text())
    description = db.Column(db.Text())
    created = db.Column(DateTime, default=datetime.utcnow())
    modified = db.Column(DateTime, default=datetime.utcnow())
    users = relationship("User", secondary='team_members')

    def __repr__(self):
        return "<Team {}>".format(self.title)
#     #creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class TeamMember(db.Model):
    """ A class for storing information about team members"""
    __tablename__ = "team_members"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team_member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # team_permissions = db.Column(db.Integer)
    user = relationship(User, backref=backref("team_members", cascade="all, delete-orphan"))
    team = relationship(Team, backref=backref("team_members", cascade="all, delete-orphan"))
    
    def __repr__(self):
        return "<TeamMember: id:{}; team_id:{}; team_member_id:{}>".format(self.id, self.team_id, self.team_member_id)
    # TODO: Implement
    #team_role_id = db.Column(db.Integer)

# class TeamRole(db.Model):
#     """ Implements team roles for team members """
#     #TODO: Lisää roolit schema.sql:n
#     __tablename__ = 'team_roles'
#     id = db.Column(db.Integer, primary_key=True)
#     role_name = db.Column(db.String(64), unique=True)
#     default_role = db.Column(db.Boolean, default=False, index=True)
#     permissions = db.Column(Integer)
#     users = relationship('User', backref='role', lazy='dynamic')

#     def __init__(self, **kwargs):
#         super(Role, self).__init__(**kwargs)
#         if self.permissions is None:
#             self.permissions = 0
    
#     def add_permission(self, perm):
#         if not self.has_permission(perm):
#             self.permissions += perm
    
#     def remove_permissions(self, perm):
#         if self.has_permissions(perm):
#             self.permissions -= perm
    
#     def reset_permissions(self):
#         self.permissions = 0
    
#     def has_permission(self, perm):
#         return self.permissions & perm == perm
    
#     def __repr__(self):
#         return '<Role %r>' % self.role_name
    
#     @staticmethod
#     def insert_roles():
#         # TODO: On lisättävä email confirmation, jotta admin-tiliä ei voida kaapata.
#         """
#         Tries to find existing roles by name and update
#         those. A new role is created only for those roles
#         that aren't in the database already. This is done
#         so the role list can be updated in the future when
#         changes need to be made.

#         This gives admission priveleges to the user who has
#         the admin email address (defined in .env in the root
#         folder). Whoever has this address, is the admin user.
#         ==> Would work better, if confirmation emails would be
#         possible to send.
#         """
#         roles = {
#             'User': [Permission.CREATE_TASKS, Permission.CREATE_GROUPS],
#             'Group role': [Permission.CREATE_TASKS,
#                 Permission.CREATE_GROUPS, 
#                 Permission.CREATE_GROUP_TASKS],
#             'Moderator': [Permission.CREATE_TASKS,
#                 Permission.CREATE_GROUPS,
#                 Permission.CREATE_GROUP_TASKS,
#                 Permission.MODERATE_GROUP],
#             'Administrator': [Permission.CREATE_TASKS,
#                 Permission.CREATE_GROUPS,
#                 Permission.CREATE_GROUP_TASKS,
#                 Permission.MODERATE_GROUP,
#                 Permission.ADMIN],
#         }
#         default_role = 'User'
#         for r in roles:
#             role = Role.query.filter_by(role_name=r).first()
#             if role is None:
#                 role = Role(role_name=r)
#             role.reset_permissions()
#             for perm in roles[r]:
#                 role.add_permission(perm)
#             role.default_role = (role.role_name == default_role)
#             db.session.add(role)
#         db.session.commit()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
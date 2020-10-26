# from . import db
from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from application import db, login_manager
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text, Boolean)
from datetime import date
from datetime import datetime
from time import time
import jwt

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
    tasks = db.relationship('Task', backref='author', lazy=True)
    # tasks = db.relationship('Task', back_populates='users')
    #tasks = db.relationship('Task', backref='user', lazy='dynamic')

    # def __init__(self, username, password):
    #     self.username = username
    #     self.password = password

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
    user = db.relationship('User')
    #user = db.relationship('User', innerjoin=True, back_populates='tasks')

    def __repr__(self):
        return "<Task {}>".format(self.body)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
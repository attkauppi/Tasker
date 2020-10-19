# from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application import db, login_manager
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from datetime import date
from datetime import datetime

class User(UserMixin, db.Model):
    """ User accont db model """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    created = db.Column(DateTime, default=datetime.utcnow())
    last_seen = db.Column(DateTime, default=datetime.utcnow())


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



class Messages(db.Model):
    """ A Model of messages table """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    def __repr__(self):
        return f"Message saved: {self.message}"


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
""" Tasker API resources """

from flask import Flask, jsonify, abort, make_response, g
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from application.models import User
from application.api.errors import forbidden#, unauthorized
from application.api import api_bp_restful

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    """ Basic auth checking for users. Allows use of
    either a token or username and password to authenticate 
    
    - if email_or_token field is empty, can't be either
    authentication method
    - if password field is empty, assume token
    - if neither field is empty, assume regular username
    password authentication.
    """
    if username_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.check_password(password)

@auth.error_handler
def unauthorized():
    """ Returns 403 instead of 401 to prevent
    browsers from displaying the default auth
    dialog """
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

@api_bp_restful.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

class AuthAPI(Resource):
    """ Authentication """

    def post(self):
        """ Receives auth """
        if g.current_user.is_anonymous or g.token_used:
            return unauthorized('Invalid credentials')
        return jsonify({'token': g.current_user.generate_auth_token(
            expiration=3600), 'expiration': 3600})

class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, location="json")


from flask import Blueprint

bp = Blueprint('api', __name__)

from application.api import errors#authentication, errors

api_bp_restful = Blueprint('api_bp', __name__)
#from application.api.resources import AuthAPI


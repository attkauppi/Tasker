from flask import Blueprint

bp = Blueprint('api_blueprint', __name__)

from application.api import errors#authentication, errors

api_bp_restful = Blueprint('api_bp', __name__)

get_blueprint = lambda: Blueprint('api_bp', __name__)
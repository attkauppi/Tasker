from flask import Blueprint

bp = Blueprint('auth', __name__)
print("Auth luokka uudessa paikassa")

from application.auth import routes
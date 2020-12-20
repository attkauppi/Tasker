from flask import Blueprint

bp = Blueprint('main', __name__)

#from application.main import routes

from application.main import routes
from application.models import Permission, TeamPermission

# TODO: et ole varma toimiiko tämä
@bp.app_context_processor
def inject_permissions():
    """
    This is to ease checking permissions in templates
    should that be necessary. In particular, to avoid
    having to add a template argument in every time
    permissions need to be checked in a template,
    we're using a context processor, which makes the
    permissions information available to all the templates
    during rendering.
    """
    return dict(Permision=Permission)

@bp.app_context_processor
def inject_team_permissions():
    """ Injects team permissions to templates """
    return dict(TeamPermission=TeamPermission)
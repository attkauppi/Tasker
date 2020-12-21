from flask import Blueprint

bp = Blueprint('main', __name__)

#from application.main import routes

from application.main import routes
from application.models import Permission, TeamPermission, User

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

@bp.app_context_processor
def utility_functions():
    """ Eases the use of certain details,
    for example, gets a user's TeamRole
    more easily, reducing the amount of code
    required in the jinja template"""

    def get_user_team_role(user, team_id):
       """ Returns a user's role in the
       team as a string """
       print("Käyttää context_processorin_menetelmää")
       return user.get_team_role(team_id)
    
    return dict(get_user_team_role=get_user_team_role)

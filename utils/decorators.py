from functools import wraps
from threading import Thread
from flask import abort
from flask_login import current_user
from application.models import Permission, TeamPermission, Team
from flask import request

#TODO: Teit tähän muutoksen ottamalla team_id:n mukaan.

def team_role_required(team_id):
    """ Decorator for ensuring user has a team role """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("request.view_args ", request.view_args)
            team_id = request.view_args.get('id')
            #print("Team_id: ", team_id)
            team = Team.query.filter_by(id=team_id).first()
            print("team.team_members: ", team.team_members)
            print("Current_user: ", current_user.id)

            if not current_user in team.users:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def team_permission_required2(id, permission):
    """ Decorator for ensuring user has a team role """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            tiimi_id_view = request.view_args.get('id')
            tiimi_rooli = current_user.get_team_role(tiimi_id_view)

            if not tiimi_rooli.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def team_moderator_required(id):
    """ Ensures that the user has at least team
    moderator privileges 
    
    TÄMÄ TOIMII 
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            #tiimi_id = request.args.get('id')
            print("View args: ", request.view_args)
            tiimi_id_view = request.view_args.get('id')

            #perms2 = request.view_args.get('permission')
            #print("tiimi id view: ", tiimi_id_view)
            #print("Request view args: ", request.view_args)
            #tiimi_id = request.args['id']
            tiimi_rooli = current_user.get_team_role(tiimi_id_view)
            # print("ID: decoraattorissa: ", tiimi_id)
            #if not current_user.can_team(tiimi_id_view, permission):
                #abort(403)
            if not tiimi_rooli.has_permission(TeamPermission.MODERATE_TEAM):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# FIXME: Rikki
def team_permission_required(permission, id):
    """ Decorator for checking team permissions """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("Decorated functionin saamat argit")
            print("Request view args: ", request.view_args)
            print(request.args)
            tiimi_id = request.args.get('id')
            tiimi_id_view = request.view_args.get('id')
            #perms2 = request.view_args.get('permission')
            print("tiimi id view: ", tiimi_id_view)
            print("Request view args: ", request.view_args)
            #tiimi_id = request.args['id']
            print("ID: decoraattorissa: ", tiimi_id)
            if not current_user.can_team(tiimi_id_view, permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# def team_moderator_required(f):
#     return team_permission_required(TeamPermission.MODERATE_TEAM)(f)

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            print("Toisen funktion view argit: ")
            print("dekoraattorin Permission: ", permission)
            print(request.view_args)
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)

def async_task(f):
    """ Takes a function and runs it in a thread """
    @wraps(f)
    def _decorated(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return _decorated
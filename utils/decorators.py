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
            team = Team.query.filter_by(id=team_id).first()
            if not current_user in team.users:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def team_permission_required(permission, team_id):
    """ Decorator for checking team permissions """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("Decorated functionin saamat argit")
            print(request.args)
            if not current_user.can_team(permission, team_id):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def team_moderator_required(f):
    return team_permission_required(TeamPermission.MODERATE_TEAM)(f)

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
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
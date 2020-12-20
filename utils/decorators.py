from functools import wraps
from threading import Thread
from flask import abort
from flask_login import current_user
from application.models import Permission, TeamPermission

def team_permission_required(permission):
    """ Decorator for checking team permissions """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can_team(permission):
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
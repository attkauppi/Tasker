from flask import Blueprint

bp = Blueprint('main', __name__)

#from application.main import routes

from application.main import routes
from application.models import Permission, TeamPermission, User, TeamTask, Team, TeamPermission, TeamMember
from flask import request
# TODO: et ole varma toimiiko tämä

# @bp.app_context_processor()
# def inject_team_id():
#     if "team" in request.endpoint:
#         return dict(Team:Team)


# @bp.app_context_processor()
# def inject_team_id():
   
#     if "team" in request.path:
#         print("Request path: ", request.path)

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

    def get_user_from_team_member_id(team_member_id, team_id):
        """ Returns user from team_member id and team id """
        print("team member id: ", team_member_id)
        print("team id: ", team_id)
        if team_member_id is None or team_id is None:
            return None
        tm = TeamMember.query.filter_by(id=team_member_id).filter_by(team_id=team_id).first()
        if tm is None:
            return None
        print("tm: ", tm)
        # FIXME: harhaanjohtava TeamMember-muuttuja
        u = User.query.filter_by(id=tm.team_member_id).first()
        print("user: ", u)
        return u

    def get_user_from_id(id):
        """ Returns user from id """
        u = User.query.filter_by(id=id).first()
        return u

    def can_modify_team_task(task, user):
        """ Returns whether a user can modify a particular
        task """
        return TeamTask.can_modify(task, user)
        # team_task = TeamTask.query.filter_by(task_id=task.id).first()
        # team_member = user.get_team_member_object(team_task.team_id)

        # if team_member.id == team_task.doing:
        #     return True
        # return False
    
    # FIXME: legacy versio, poista
    def get_task_assigned(team_task):
        """ Returns a boolean value depending on 
        whether the team task has been assigned to someone """
        print("team_task: ", team_task)
        print("Team_task ")
        team_task = team_task[0]
        print("team_task id: ", team_task.id)
        #team_task_id = team_task.id
        team_task = TeamTask.query.filter_by(id=team_task.id).first()
        return team_task.doing
        
        #return team_task.get_doing()
    
    # FIXME: Nimeä uudelleen
    def get_task_assigned2(team_task):
        """ Returns a boolean value depending on 
        whether the team task has been assigned to someone """
        print("team_task: ", team_task)
        print("Team_task ")
        team_task = team_task[0]
        print("team_task id: ", team_task.id)
        #team_task_id = team_task.id
        team_task = TeamTask.query.filter_by(id=team_task.id).first()
        if team_task is None:
            return None
        return team_task
    
    def get_user_team_role(user, team_id):
       """ Returns a user's role in the
       team as a string """
       print("Käyttää context_processorin_menetelmää")
       return user.get_team_role(team_id)
    
    return dict(
        get_user_team_role=get_user_team_role,
        get_task_assigned=get_task_assigned,
        get_user_from_id=get_user_from_id,
        can_modify_team_task=can_modify_team_task,
        get_user_from_team_member_id=get_user_from_team_member_id,
        get_task_assigned2=get_task_assigned2
    )

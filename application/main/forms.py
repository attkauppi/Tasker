from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, Email, Regexp
from application.models import User, Team, Role, TeamRole, Board, Task, TeamPermission, TeamMember, TeamTask
from flask_pagedown.fields import PageDownField


class EditProfileForm(FlaskForm):
    """ Form for handling user profile edits """
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=360)])
    email = StringField("Email", [DataRequired('Please enter your email address.'),
        Email('This field requires a valid email address')])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        """ Validates a user's username """
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(message='Please choose another username.')

class EditProfileAdmin(FlaskForm):
    """ Form for admins to edit user profile fields. """
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    # name = StringField('Name', validators=[Length(0, 64)])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=360)])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdmin, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.role_name)
                            for role in Role.query.order_by(Role.role_name).all()]
        self.user = user
    
    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise(ValidationError("Email already registered."))
    
    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")

# class EmptyForm(FlaskForm):
#     """ A class that's going to be used for
#     events that only require a click of a button.
#     These are implemented as POST requests to avoid
#     the danger of CSRF attacks associated with GET-requests """
#     # TODO these will be used for 
#     submit = SubmitField('Submit')

# class PostForm(FlaskForm):
#     """ These may be used for comments """
#     post = TextAreaField('Say something', validators=[DataRequired()])
#     submit = SubmitField('Submit')

class EmptyForm(FlaskForm):
    """ Used for forms with only a button """
    submit = SubmitField('Submit')

class TaskForm(FlaskForm):
    """ Used to create tasks """
    # TODO: Saatat joutua muuttamaan myöhemmin, mikäli ryhmien luomia tehtäviä varten.
    task_title = TextAreaField('Task title', validators=[DataRequired()])
    task_description = TextAreaField('Task description', validators=[DataRequired()])
    done = BooleanField('Task done?', default=False)
    submit = SubmitField('Create/Edit')

class TeamDeleteForm(FlaskForm):
    """ Form for deleting team """
    submit = SubmitField('Delete team')

class TeamCreateForm(FlaskForm):
    """ Used to create teams """
    title = TextAreaField('Team name', validators=[DataRequired()])
    description = TextAreaField('Team description', validators=[DataRequired()])
    submit = SubmitField('Create/Edit')

class TeamEditForm(FlaskForm):
    """ Used to edit teams """
    title = TextAreaField('Team name', validators=[DataRequired()])
    description = TextAreaField('Team description', validators=[DataRequired()])
    submit = SubmitField('Create/Edit')

class TeamInviteForm(FlaskForm):
    """ Form used to invite new members to Team """
    submit = SubmitField('Invite')


class TeamEditMemberForm(FlaskForm):
    """ Form for editing team member roles """
    team_role = SelectField('Team role', coerce=int)
    submit = SubmitField('Save changes')
    
    
    def __init__(self, max_role_id, *args, **kwargs):
        super(TeamEditMemberForm, self).__init__(*args, **kwargs)
        #self.team_role_choices = 
        #self.team_role.choices = [(team_role.id, team_role.team_role_name)
        #    for team_role in TeamRole.query.order_by(TeamRole.id).all()]
        team_roles = TeamRole.query.all()
        current_role = TeamRole.query.filter_by(id=max_role_id).first()
        #choices = []
        #for i in self.team_role.choices:
        team_role_choices = []
        for i in team_roles:
            #print("Maksimiroolin määrittelyn kummallinen merkintä; ", i[0])
            print("team roles: ", i)
            if i.team_permissions <= current_role.team_permissions:
                
                team_role_choices.append((i.id, i.team_role_name))

        self.team_role.choices = team_role_choices
        

class TeamTaskForm(FlaskForm):
    """ Form for creating team tasks """
    title = TextAreaField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    
class TeamTaskFormEdit(FlaskForm):
    """ Form for creating team tasks """
    title = TextAreaField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    assign_to_choices = SelectField('Team member', coerce=int, choices=[(1, "TODO"), (2, "DOING"), (4, "DONE")])
    board_choices = SelectField('Move to board', coerce=int, default=0, choices=[(1, "TODO"), (2, "DOING"), (4, "DONE")])
    
    
    def __init__(self, team_id, task, user, *args, **kwargs):
        super(TeamTaskFormEdit, self).__init__(*args, **kwargs)
        lista = []

        team = Team.query.filter_by(id=team_id).first()

        team_members = team.team_members
        team_task = TeamTask.query.filter_by(task_id=task.id).first()

        # Lista pohjana muille osuuksille
        lista3 = []
        
        for i in team_members:
            if team_task.doing is not None and team_task.doing == i.team_member_id:
                lista3.insert(0, (i.team_member_id, i.team_member_user.username))

            else:
                lista3.append((i.team_member_id, i.team_member_user.username))

        # If task not assigned to anyone, set None as default in the field
        if team_task.doing is None:
            lista3.insert(0, (0, "None"))
        else:
            lista3.append((0, "None"))

        if not user.can_team(team_id, TeamPermission.ASSIGN_TASKS):

            if team_task.doing is None:
                lista3 = [(0, "None"), (user.id, user.username)]
            else:
                if team_task.doing != user.id:
                    # Ei tee tehtävää, mutta joku muu on määritelty tekemään
                    team_member = TeamMember.query.filter_by(team_member_id=team_task.doing).first()
                    lista3 = [(team_member.team_member_id, team_member.team_member_user.username)]
                else:
                    # tekee tehtävää
                    lista3 = [(user.id, user.username), (0, "None")]

        self.assign_to_choices.choices = lista3
        print("self.assign_to_choices: ", self.assign_to_choices)

        # Find the team_task that corresponds to the task object
        team_task = TeamTask.query.filter_by(task_id=task.id).first()
        # Get the team_member curerntly doing the task

        # If someone is already doing/assigned the task, we need to
        # set them as the default choice in the form.
        if team_task.doing is not None:
            team_member = TeamMember.query.filter_by(id=team_task.doing).first()

        lista2 = []
        for item in Task.boards().items():
            lista2.append((item[1], item[0]))
        board_choices = self.get_board_choices()
        default_value = self.get_default_value_for_board_choices(task, board_choices)
        board_choices_default_first = self.get_board_choices_with_default_first(default_value, board_choices)

        self.board_choices.choices = board_choices_default_first

    def get_board_choices(self):
        """ Generates a list of tuples for board choices """
        # Task.boards() gives us the values we need, but in the wrong
        # order (board name, board id), we want them as (board id, board name)
        boards_dict = {y:x for x,y in Task.boards().items()}
        # print("Boards dict: ", boards_dict)

        # Now we can generate a list of choices for the selectfield
        # and have the current board as the default choice
        list = [(k, v) for k, v in boards_dict.items()]
        return list
    
    def get_default_value_for_board_choices(self, task, list):
        """ Finds out which board the task is currently set to
        and gets us that item from the list """
        default_value = None

        for i in list:
            if i[0] == task.board:
                default_value = i
        
        return default_value
    
    def get_board_choices_with_default_first(self, default_value, list):
        """ Generates a new list of choices, where the default value is
        the first item and returns the list """
        list2 = []

        default_added = False
        
        
        while len(list) > 0:
            for i in list:
                if not default_added:
                    if i[0] == default_value[0] and i[1] == default_value[1]:
                        list2.append(i)
                        default_added = True
                        list.remove(i)
                        break
                    continue
                list2.append(i)
                list.remove(i)
        
        return list2
    
    def get_assign_to_choices_with_default_first(self, task, team):

        # Find the team_task that corresponds to the task object
        team_task = TeamTask.query.filter_by(task_id=task.id).first()
        default_value = None
        if team_task.doing is not None:
            team_member = TeamMember.query.filter_by(id=team_task.doing).first()
            default_value = team_member
        list = team.team_members

        list2 = []

        default_added = False

        

        if len(list) == 1:
            list2.append((list[0].team_member_id, list[0].team_member_user.username))
            print("list2 metodin lopussa?: ", list2)
            return list2
        
        while len(list) > 0:
            for i in list:
                if not default_added:
                    if i.team_member_id == team_task.doing:

                        list2.append((i.team_member_id, i.team_member_user.username))
                        default_added = True
                        list.remove(i)
                        break
                    continue
                list2.append((i.team_member_id, i.team_member_user.username))
                list.remove(i)
        return list2


class TeamTaskSendToBoard(FlaskForm):
    """ Sends a task to another board """
    submit = SubmitField('Send to board')


class TestForm(FlaskForm):
    """ Test Form """
    vastaanottaja = TextAreaField('Vastaanottaja', validators=[DataRequired()])
    viesti = TextAreaField('Viesti', validators=[DataRequired()])
    submit = SubmitField('Tee jotain')

# TODO: Uusi message-luokka käytössä
class MessageForm(FlaskForm):
    """ Form for sending messages - new message class"""
    message = TextAreaField(('Message'), validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('submit-comment')
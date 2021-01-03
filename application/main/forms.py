from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, Email, Regexp
# from flask_babel import _, lazy_gettext as _l
from application.models import User, Role, TeamRole, Board, Task


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
            # SQL
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
    #TODO: Ota käyttöön, kun sähköpostivarmistaminen toimii
    # confirmed = BooleanField('Confirmed)
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
    # TODO: Lisättävä kai selectfield, johon määritetään roolit/permissionit? Vrt. EditProfileAdmin-lomakkeeseen.
    #team_role = SelectField('Team role', coerce=int)
    submit = SubmitField('Invite')

    # def __init__(self, *args, **kwargs):
    #     super(TeamInviteForm, self).__init__(*args, **kwargs)
    #     self.team_role.choices = [(team_role.id, team_role.team_role_name)
    #         for team_role in TeamRole.query.order_by(TeamRole.team_role_name).all()]
        #self.user = user
    
    #def validate_email(self, field):
    #    if field.data != self.user.email and User.query.filter_by(email=field.data).first():
    #        raise(ValidationError("Email already registered."))

class TeamEditMemberForm(FlaskForm):
    """ Form for editing team member roles """
    team_role = SelectField('Team role', coerce=int)
    submit = SubmitField('Save changes')
    
    
    def __init__(self, max_role_id, *args, **kwargs):
        super(TeamEditMemberForm, self).__init__(*args, **kwargs)
        #self.team_role_choices = 
        self.team_role.choices = [(team_role.id, team_role.team_role_name)
            for team_role in TeamRole.query.order_by(TeamRole.id).all()]
        
        for i in self.team_role.choices:
            if i[0] > max_role_id:
                self.team_role.choices.remove(i)
        
        print(self.team_role.choices)
        print("max role: ", max_role_id)
        #for i in self.team_role.choices:
        #    if i.team_permissions > max_role.permissions:
        #        self.team_role.choices.remove(i)
        #print("Team edit member formin roolit: ", self.team_role.choices)
        #print("sovelluksen käyttäjän rooli: ", user)

class TeamTaskForm(FlaskForm):
    """ Form for creating team tasks """
    title = TextAreaField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    #board = SelectField('Team role', coerce=int)


    # def __init__(self, board_id, *args, **kwargs):
    #     super(TeamTaskForm, self).__init__(*args, **kwargs)
    #     #self.team_role_choices = 
    #     board_names = ["Todos", "Doing", "Done"]

    #     self.board.choices = [(, board_name)
    #         for board_name in board_names]
        
        # for i in self.team_role.choices:
        #     if i[0] > max_role_id:
        #         self.team_role.choices.remove(i)
        
        # print(self.team_role.choices)
        # print("max role: ", max_role_id)
    #priority = BooleanField('Give priority')
    # board valinta?
    #submit = SubmitField('submit')
    
class TeamTaskFormEdit(FlaskForm):
    """ Form for creating team tasks """
    title = TextAreaField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    #board = SelectField('Team role', coerce=int)
    assign_to_choices = SelectField('Team member', coerce=int)
    # FIXME: Korjattava dynaamiseksi
    board_choices = SelectField('Move to board', choices=[(1, "TODO"), (2, "DOING"), (4, "DONE")])
    
    
    def __init__(self, team, task, *args, **kwargs):
        super(TeamTaskFormEdit, self).__init__(*args, **kwargs)
        #self.team_role_choices = 
        lista = []
        for member in team.team_members:
            lista.append((member.team_member_user.id, member.team_member_user.username))
        print("lista: ", lista)

        lista2 = []

        print(args)
       
        print("type boards: ", type(Task.boards()))

        
        lista2 = []
        for item in Task.boards().items():
            print("Item key: ", item[0])
            print("item value: ", item[1])
            lista2.append((item[1], item[0]))
        
        #self.board_choices = [("TODO": 1), ("DIONG"]#[(i.value, i.key) for i in Task.boards()]

        #print("Task boards; ", task.boards())
        print("Board choices: ", self.board_choices)
        #self.board_choices = ([task.board, ])
        self.assign_to_choices.choices = lista
        print("self.assign_to_choices: ", self.assign_to_choices)
        
        #self.move_to_board_choices = [(1, "todo"), (2, "doing"), (3, "done")]

        # self.assign_to_choices.choices = [(team.team_members.team_member_user.id, team.team_members.team_member_user.username)
        #     for team_member in team.team_members.team_member_user]

        # self.team_.choices = [(team_members.id, team_members.username)
        #     for team_member in team_members]
        


    # def __init__(self, user, *args, **kwargs):
    #     super(EditProfileAdmin, self).__init__(*args, **kwargs)
    #     self.role.choices = [(role.id, role.role_name)
    #                         for role in Role.query.order_by(Role.role_name).all()]
    #     self.user = user

class TeamTaskSendToBoard(FlaskForm):
    """ Sends a task to another board """
    submit = SubmitField('Send to board')



class TestForm(FlaskForm):
    """ Test Form """
    vastaanottaja = TextAreaField('Vastaanottaja', validators=[DataRequired()])
    viesti = TextAreaField('Viesti', validators=[DataRequired()])
    submit = SubmitField('Tee jotain')

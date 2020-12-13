from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, Email, Regexp
# from flask_babel import _, lazy_gettext as _l
from application.models import User, Role


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
    #name = StringField('Name', validators=[Length(0, 64)])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=360)])

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdmin, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.role_name)
            for role in Role.query.order_by(Role.role_name).all()]
    
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

class TaskForm(FlaskForm):
    """ Used to create tasks """
    # TODO: Saatat joutua muuttamaan myöhemmin, mikäli ryhmien luomia tehtäviä varten.
    task_title = TextAreaField('Task title', validators=[DataRequired()])
    task_description = TextAreaField('Task description', validators=[DataRequired()])
    done = BooleanField('Task done?', default=False)
    submit = SubmitField('Create/Edit')


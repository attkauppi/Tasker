from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Length, Email
# from flask_babel import _, lazy_gettext as _l
from application.models import User


class EditProfileForm(FlaskForm):
    """ Form for handling user profile edits """
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=360)])
    email = StringField("Email", [DataRequired('Please enter your email address.'), Email('This field requires a valid email address')])
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
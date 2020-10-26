from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from application.models import User


class LoginForm(FlaskForm):
    """ Form for the login function """
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """ Form for registration """
    username = StringField('Username')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired(), EqualTo('password2')])
    password2 = PasswordField('Repeat password')#, validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Register')

    def validate_username(self, username):
        """ Validates username not already in use """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(message='Please choose another username!')

    def validate_email(self, email):
        """ Validates that the email isn't already
        in use. """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use another email address.")

class ResetPasswordRequestForm(FlaskForm):
    """ A form for requesting a password reset """
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Request password reset")

class ResetPasswordForm(FlaskForm):
    """ A form for resetting password """
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2')])
    password2 = PasswordField('Repeat password', validators=[DataRequired()])
    # TODO: Jos tulee ongelmia, muutit seuraavan nimen
    submit = SubmitField('Reset password')


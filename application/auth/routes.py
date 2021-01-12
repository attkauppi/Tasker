from flask import render_template, redirect, url_for, flash, request, session, g
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from application import db, login_manager
from application.auth import bp
from application.auth.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordRequestForm,
    ResetPasswordForm
)
from application.auth.email import send_password_reset_email, send_confirmation_email
from application.models import User
from datetime import date
from datetime import datetime
from application.email import send_email
import os

@bp.before_app_request
def before_request():
    """ before_app_request handler will intercept a
    request when 3 conditions are true

    1. A user is logged in (current_user.is_authenticated is True)
    2. The account for the user is unconfirmed
    3. The request URL is outside of the authentication blueprint
    and is not for a static file. Access to the authentication
    routes needs to be granted, as those are the routes that
    will enable the user to confirm the account or perform other
    account management functions.

    When these 3 conditions are met, a redirect is issued to a new
    /auth/unconfirmed route that shows a page with information about
    account confirmation. 
    """
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@bp.before_request
def before_request():
    if 'DYNO' in os.environ:
        if request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            code = 301
            return redirect(url, code=code)

@bp.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()        
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    """ Handles logging out """
    session.clear()
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():

        user = None
        
        # If EMAIL_CONFIGURED environment variable is set
        # to false, all users are confirmed upon registration.
        # this is risky, because the only thing keeping someone
        # from highjacking the admin account is the registered
        # email addresses of users having to be confirmed.
        if os.getenv('EMAIL_CONFIGURED') != 0 and os.getenv('EMAIL_CONFIGURED') is not None:

            user = User(
                username=form.username.data,
                email=form.email.data.lower(), 
                confirmed=True
            )
            
        else:
            user = User(
                username=form.username.data,
                email=form.email.data.lower(),
                created = datetime.utcnow())
        
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Token for email confirmation email
        if os.getenv('EMAIL_CONFIGURED') != 0:
            send_confirmation_email(user)
            token = user.generate_confirmation_token()

        user_new = User.query.filter_by(username=user.username).first()
        flash("Congrats, you're now a user! We sent a confirmation link to your email.")
        return redirect(url_for("auth.login"))
    return render_template('auth/register.html', form=form)

@bp.route('/reset_password_request', methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if request.method == "POST":
        if form.validate_on_submit:
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                send_password_reset_email(user)
            flash('Check your email for instructions')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)

@bp.route('reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verity_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@bp.route('/confirm/<token>', methods=["GET", "POST"])
@login_required
def confirm(token):
    """Used to confirm token sent to user after
    registering to site.

    Args:
        token ([type]): [description]
    """
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        # Current user's confirm field
        # is set to True in database. User was added
        # to be saved in the models confirm-method of
        # the user database model.
        db.session.commit()
        flash('You have confirmed your account! Welcome to Tasker!')
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for('main.index'))

@bp.route('/confirm')
@login_required
def resend_confirmation():
    """ Used to resend confirmation to user, if the
    confirmation sent earlier has expired or is invalid """
    send_confirmation_email(current_user)
    flash('A new confirmation email has been sent to your email address.')
    return redirect(url_for('main.index'))
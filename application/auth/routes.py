from flask import render_template, redirect, url_for, flash, request, session, g
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from application import db, login_manager
from application.auth import bp
from application.auth.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordRequestForm,
    ResetPasswordForm
)
from application.auth.email import send_password_reset_email
from application.models import User
from datetime import date
from datetime import datetime


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
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        user.email = form.email.data
        user.created = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash("Congrats, you're now a user")
        return redirect(url_for("auth.login"))
    return render_template('auth/register.html', form=form)

@bp.route('/reset_password_request', methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        print("Authenticated")
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if request.method == "POST":
        if form.validate_on_submit:
            user = User.query.filter_by(email=form.email.data).first()
            print("User", user)
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

from flask import render_template, redirect, url_for, flash, request, session, g
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from application import db, login_manager
from application.auth import bp
from application.auth.forms import LoginForm, RegistrationForm
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
        user.created = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash("Congrats, you're now a user")
        return redirect(url_for("auth.login"))
    return render_template('auth/register.html', form=form)
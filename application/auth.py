import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from application.db import db
from flask_login import current_user, login_required
from . models import User
from . import login_manager

bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


def login_required(view):
    """ Checks if a user is logged in """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# @bp.before_app_request
# def load_logged_in_user():
#     """ Ei tietoa toimiiko """
#     user_id = session.get('user_id')

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = db.session.execute(
#             'SELECT * FROM users WHERE id = ?', (user_id,)
#         ).fetchone()

def login_aux(username, password):
    """
    Auxiliary login method'
    
    Verifies whether user's login attempt
    was valid.
    """
    sql = "SELECT password, id FROM users WHERE username=:username"
    # Haetaan käyttäjän salasana
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    print("user[0]: ", user[0])
    print("user[1]: ", user[1])
    # print("USER: ")
    # print(user[0])

    # Mikäli käyttäjänimellä ei löytynyt ylipäänsä salasanaa,
    # käyttäjä ei ole rekisteröitynyt.
    if user == None:
        return False
    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password):
            print("User: ", user[0], user[1])
            session['user_id'] = user[1]
            return True
        else:
            return False

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if login_aux(username, password):
            session["username"] = username
            print("Session: ", session)
            print("Session username: ", session["username"])
            return redirect("/")
        else:
            error = "Kirjautuminen epäonnistui"
            flash(error)
            # TODO: Implementoi error.html
            # return render_template("error.html",message="Väärä tunnus tai salasana")
    # return render_template("auth/login.html")

@bp.route('/logout')
def logout():
    # session.clear()
    # return redirect(url_for('index'))
    # del session["username"]
    print("Session: ", session)
    print("Session username: ", session["username"])
    username = session["username"]
    print("KEYT")
    session.clear()
    return redirect("/")

def register_aux(username, password):
    """ Handles actual registering """
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password) VALUES (:username,:password)"
        db.session.execute(sql, {"username":username,"password":hash_value})
        db.session.commit()
    except:
        return False
    return login_aux(username,password)

# def login(username, password):
def user_id():
    return session.get("user_id",0)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
        # return redirect(url_for('auth.login'))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print("USERNAME: ", username)
        print("PASSWORD: ", password)
        
        if register_aux(username, password):
            return redirect("/auth/login")
        else:
            return render_template("error.html",message="Rekisteröinti ei onnistunut")
        

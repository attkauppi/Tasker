from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from application import db, login_manager
from application.main.forms import TaskForm, EditProfileForm, EditProfileAdmin, TeamCreateForm, TeamEditForm#, EmptyForm, PostForm
from application.models import User, Task, Role, Team, TeamMember
from application.main import bp
from utils.decorators import admin_required

print("Main luokka")
# @login_manager.user_loader
# def load_user(user_id):
#     """Check if user is logged-in on every page load."""
#     if user_id is not None:
#         return User.query.get(user_id)
#     return None


# def login_required(view):
#     """ Checks if a user is logged in """
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))

#         return view(**kwargs)

#     return wrapped_view

#@bp.before_app_request
#def before_request():
#    if current_user.is_authenticated:
#        current_user.last_seen = datetime.utcnow()
#        db.session.commit()
#    g.locale = str(get_locale())
@bp.before_app_request
def before_request():
    print("Before request")
    if current_user.is_authenticated:
        # This uses utcnow for consistency. A user
        # may be located wherever, but utcnow won't
        # care. datetime.now(), however, would.
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    
    # TODO: If there's time, you might want to implement locales.
    # g.locale = str(get_locale())

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    print("Index metodi")
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    # TODO Kesken.
    # form = PostForm()
    # TODO Validate form if used
    # Redirect user to the page they were trying to access
    # page = request.args.get('page', 1, type=int)
    # print("page: ", page)
    # Get messages
    result = db.session.execute("SELECT COUNT(*) FROM messages")
    count = result.fetchone()[0]
    result = db.session.execute("SELECT content FROM messages")
    messages = result.fetchall()

    # user_agent = request.headers.get('User-Agent')
    return render_template("index.html", count=count, messages=messages)

@bp.route("/new")
def new():
    return render_template("new.html")

@bp.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    sql = "INSERT INTO messages (content) VALUES (:content)"
    db.session.execute(sql, {"content":content})
    db.session.commit()
    return redirect("/")

@bp.route('/user/<username>', methods=["GET", "POST"])
@login_required
def user(username):

    user = User.query.filter_by(username=username).first_or_404()
    print("Parametrina saatu user: ", user)
    print("Nykyinen kayttaja: ", current_user.username)
    # ==> Eroavat toisistaan
    
    # TODO: Onko teoriassa mahdollista, että toinen käyttäjä voisi lisätä tehtäviä toiselle? Kokeile esim. Postmanilla.
    form = TaskForm()
    if form.validate_on_submit() and username == current_user.username:
        title=form.task_title.data
        description=form.task_description.data
        task = Task(
            title=form.task_title.data,
            description=form.task_description.data,
            done = form.done.data,
            creator_id = current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash("Added task, hopefully.")
        return redirect(url_for('main.user', username=current_user.username))

    page = request.args.get('page', 1, type=int)

    user_tasks = user.tasks
    
    # Testidata, jolla saa testattua helposti, mikäli hajoaa jossain
    # vaiheessa: 
    #tasks = [
    #    {'author': user, 'title': 'Test task1'},
    #    {'author': user, 'title': 'Test task2'}
    #
    #]

    # TODO: Ei kannata toteuttaa kai näin, vaan esim. käytttämällä rooleja.
    # Tosin kannattaa miettiä, miten sivustot suunnittelee.
    if user.username != current_user.username:
        return render_template('user.html', user=user, tasks=user_tasks)
    return render_template('user.html', user=user, tasks=user_tasks, form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """ Allows making changes to a user profile """
    # TODO: There's no test for this method yet.
    form = EditProfileForm(current_user.username)
    # TODO: SQL-komennot tilalle lopuksi

    # FIXME: Salli myös salasanan vaihtaminen
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.email = form.email.data.lower()
        db.session.commit()
        flash('Your profile was edited!')
        return redirect(url_for('main.edit_profile'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.email.data = current_user.email
    return render_template('edit_profile.html', title=('Edit Profile'), form=form)

@bp.route('/edit_profile/<int:id>', methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    """ Route that allows admin to edit user profiles """
    user = User.query.get_or_404(id)
    print(user)
    form = EditProfileAdmin(user=user)
    # POST-pyynnön tapahduttua
    if form.validate_on_submit():
        user.email = form.email.data.lower()
        user.username = form.username.data
        # TODO: Lisää, kun sähköpostivarmistus toimii
        #user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        # TODO: lisää jos otat nimet käyttöön
        # user.name = form.name.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated')
        #FIXME: Voi olla että tämä ei toimi
        return redirect(url_for('.user', username=user.username))
    # Get-pyyntöä tehdessä, haetaan valmiiksi käyttäjän tiedot kenttiin
    form.email.data = user.email
    form.username.data = user.username
    # form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    # form.name.data = user.name
    form.about_me = user.about_me
    print(user)
    return render_template('edit_profile.html', title=('Edit Profile'), form=form, user=user)

@bp.route('/teams/create_team', methods=["GET", "POST"])
@login_required
def create_team():
    """ Allows creating a new team """
    form = TeamCreateForm()
    
    if form.validate_on_submit():
        team = Team(
            title = form.title.data,
            description = form.description.data
        )
        db.session.add(team)
        db.session.commit()

        # Get the current team's id now that it has
        # been assigned
        t = Team.query.filter_by(title=team.title).first()

        # Create team_member association table record
        team_member = TeamMember(
            team_id = t.id,
            team_member_id = current_user.id
        )

        db.session.add(team_member)
        db.session.commit()

        flash("Your team was created!")
        return redirect(url_for('main.team', id=t.id))#title=(team.title), team_id=t.id))
    
    return render_template('edit_team.html', title=("Create your team"), form=form)

@bp.route('/teams/<int:id>/edit_team', methods=["GET", "POST"])
@login_required
def edit_team(id):
    """ edit team form """
    team = Team.query.get_or_404(id)
    form = TeamEditForm()

    if form.validate_on_submit():
        team.title = form.title.data
        team.description = form.description.data
        team.modified = datetime.utcnow()

        db.session.add(team)
        db.session.commit()

        flash('Your team was updated!')
        return redirect(url_for('main.team', id=team.id))

    form.title.data = team.title
    form.description.data = team.description
    
    return render_template('edit_team.html', title=("Edit your team"), form=form)

@bp.route('/teams/<int:id>/invite', methods=["GET", "POST"])
@login_required
def invite_to_team(id):
    team = Team.query.get_or_404(id)
    users = User.query.all()

    return render_template('find_user.html', id=id, users=users)


@bp.route('/team/<int:id>', methods=["GET", "POST"])
@login_required
def team(id):
    #team = Team.query.filter_by(id=team_id).first_or_404()
    team = Team.query.get_or_404(id)

    team_members = team.users
    print("Team members")
    for i in team_members:
        
        print(i)

    
    return render_template('team.html', team=team)

from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from application import db, login_manager
from application.main.forms import (
    TaskForm, EditProfileForm, EditProfileAdmin, TeamCreateForm, TeamEditForm,
    TeamInviteForm,
    TeamEditMemberForm
)#, EmptyForm, PostForm
from application.models import User, Task, Role, Team, TeamMember, TeamRole, TeamPermission
from application.main import bp
from utils.decorators import (
    admin_required,
    permission_required,
    team_moderator_required,
    team_permission_required
)
from sqlalchemy.orm import session
from sqlalchemy import and_, or_, not_, MetaData
meta = MetaData()
from flask import request
from flask import abort


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

@bp.route("/shutdown")
def server_shutdown():
    """ needed for selenium testing """
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return('Shutting down')

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

    print("user teams: ")
    print(user.teams)
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
        user.confirmed = form.confirmed.data
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
    form.confirmed.data = user.confirmed
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

        tr = TeamRole.query.filter_by(id=4).first()

        # Create team_member association table record
        team_member = TeamMember(
            team_id = t.id,
            team_member_id = current_user.id,
            team_role_id = tr.id
        )

        db.session.add(team_member)
        db.session.commit()

        tm_uusi = TeamMember.query.filter_by(team_id=t.id).first()
        print("TM UUSI: ", tm_uusi)

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
    """ Route of endpoint for sending
    team """
    team = Team.query.get_or_404(id)
    users = User.query.all()

    # Filters out the users already in the team
    # TODO: Write a better method to do this that doesn't
    # constantly fail like the other methods you tried. 
    us = []
    for i in users:
        if team in i.teams:
            print("Tiimi on jo käyttäjän tiimeissä, ei lisätä")
            #continue
        else:
            us.append(i)
    
    form = TeamInviteForm()
    print("invite_to_team id: ", id)
    print("Team johon kutsutaan: ", team)
    #form = TeamInviteForm()

    if form.validate_on_submit():
        args = request.args.to_dict()
        print("post args ", args)
        return redirect(url_for('main.invite_user_to_team', team_id=str(id), username=form.username.data))

    if not us:
        flash("Sorry, we've run out of users, it seems\
        You could always invite your friend to join the service :-)")

    return render_template('find_user.html', team_id=id, users=us)

@bp.route('/user/<username>/popup/<int:team_id>')
@login_required
def user_popup(username, team_id):
    """ Used to create a popup window for inviting team members """
    #if path is not None:
    #    print("path: ", path)
    print("popuin team_id: ", team_id)
    print("popupin saama username: ", username)
    args = request.args.to_dict()
    print("popup args: ", args)

    form = TeamInviteForm()
    
    # print("query string: ")
    # print(request.query_string)
    user = User.query.filter_by(username=username).first_or_404()
    

    args = request.args.to_dict()

    print("popup args: ", args)

    if "team_id" in args:
        print("team id on query parametri")
    ##team_id = args.get('team_id')
    #team_id = args.get('team_id')
    #print("TEAM_ID: ", team_id)
    team = Team.query.filter_by(id=team_id).first()
    #print("team: ", team)
    #print("TEAM_ID: ", team_id)
    d = {
        "team_id": team_id,
        "username": user.username
    }
    print("d: ", d)
    #d['team_id'] = str(team_id)
    #d['username'] = user.username

    #d = dict()
    
    form = TeamInviteForm()
    #form.team_role.data = 
    #if request.method == "POST":
    #    #

    return render_template('user_popup.html', user=user, team_id=team_id, data=d, form=form)

@bp.route('/invite/<username>/<team_id>/', methods=['GET', 'POST'])
#@bp.route('/teams/<int:id>/invite/<username>', methods=["GET", "POST"])
@login_required
def invite_user_to_team(username, team_id):#username, team_id):
    """ Invites a user to a team """
    print("invite_user_to_team________________")
    print("username: ", username)
    print("team_id: ", team_id)
    args = request.args.to_dict()
    #if request.method == "POST":
        #print(request.args)
    print(args)
    print("invite_user_to_team==========")
    print(request.args)
    print("path: ")
    print(request.url.rstrip("?"))
    #print(foo)
    #args = request.args.to_dict()
    
    #print("all args: ", request.args.lists())
    args = request.args.to_dict()
    print("args: ", args)
    
    team = Team.query.filter_by(id=team_id).first()
    print("Team: ", team)
    #user = User.query.filter_by(username=username).first()
    #print("invite_user_to_team args")
    #print(args)
    #team_id = args.get('team_id')
    user = User.query.filter_by(username=username).first_or_404()
    #print("Team id: ", team_id)
    #team = Team.query.filter_by(id=team_id).first()
    #team
    print("Team johon kutsutaan: ", team)
    form = TeamInviteForm()

    if form.validate_on_submit():
        print("Forimin saama rooli määritys: ")
        print("Validoi ")
        #user = User.query.filter_by(username=username).first()
        #if user == current_user:
        #    flash("You cannot invite yourself")
        #    return redirect(url_for('main.invite_to_team', id=team.id))
        tm = team.invite_user(user.username)

        # If invite was successful, carry out
        # database operation.
        if tm:
            db.session.add(tm)
            db.session.commit()
        else:
            flash('Did you try to invite someone already in your team?')
            return redirect(url_for('main.invite_to_team', id=team.id))
        
        flash(message=('Invited user ' + user.username))
        print("Suoritus loppumassa iffin sisäiseen redirectiin")
        return redirect(url_for('main.invite_to_team', id=team.id))
    print("Suoritus loppumassa render_templateen")
    #return render_template(url_for('main.invite_to_team', id=team.id))
    return redirect(url_for('main.invite_to_team', id=team.id))


@bp.route('/team/<int:id>', methods=["GET", "POST"])
@login_required
def team(id):
    #team = Team.query.filter_by(id=team_id).first_or_404()
    

    print("Current user teams: ")
    print(current_user.teams)
    print("Current user team_members")
    print(current_user.team_memberships)
    team = Team.query.get_or_404(id)

    print("TEAM MEMBERS")
    print(team.team_members)

    # print("=======")
    # print("Tiimin nykyiset jäsenet")
    # for i in team.users:
    #     print("\t", i, " (id=",i.id,")", " Rooli tiimissä: ", i.get_team_role(team.id))
    #     print("\t\t tiimiläisetn team_member-olio: ", i.get_team_member_object(team.id))

    print("current_user team_memberships")
    print(current_user.team_memberships)

    print("membership tyypit:")
    for i in current_user.team_memberships:
        print("\t", type(i))
    tm = TeamMember.query.filter_by(team_id=id)

    print("user metodin testaus")
    tm = current_user.get_team_member_object(id)
    print("user is moderator? ", tm.is_team_moderator())

    # print("current user can moderate?")
    print(current_user.can_team(id, TeamPermission.CREATE_TASKS))
    if current_user.can_team(id, TeamPermission.CREATE_TASKS):
        print("Kayttaja saa luoda tehtavia!")

    if current_user.is_team_role(id, "Team member"):
        print("Kayttajalla on perus tiimiläisen oikeudet!")
    #meta.Session.query(Team)

    tm1 = TeamMember.query.filter_by(team_id=id).filter_by(team_member_id=current_user.id).first()
    print(tm1)

    print("type tm1: ", type(tm1))
    print("queryn tulos: ", tm1)

    team_members = team.users
    print("Team members")
    #for i in team_members:
    #    
    #    print(i)

    print("=====================")
    print("Käyttäjien roolien palauttaminen uudella metodilla: ")
    for u in team.users:
        r = u.get_team_role(team.id)
        print("\t rooli: ", r)
        

    return render_template('team.html', team=team)

@bp.route('/team/<int:id>/members', methods=["GET", "POST"])
@login_required
def team_members(id):
    """ Allows editing member roles """
    team = Team.query.get_or_404(id)

    print("Team users")
    return render_template('team_members.html', team=team, users=team.users)

@bp.route('/team/<int:id>/members/edit/<username>', methods=["GET", "POST"])
@login_required
# FIXME: Lisättävä, kun saat toimimaan.
#@team_permission_required(id, TeamPermission.MODERATE_TEAM)
def edit_team_member(id, username):
    """ Allows editing a team members team details """
    team = Team.query.get_or_404(id)
    user = User.query.filter_by(username=username).first()

    # Any user should not be able to assign a role higher than
    # they already have to anyone else.
    max_role = current_user.get_team_role(id)

    max_role_id = current_user.get_team_member_object(id).team_role_id
    print(max_role_id)

    form = TeamEditMemberForm(max_role_id=max_role_id)

    if form.validate_on_submit():
        user_team_member_object = user.get_team_member_object(id)
        print("Team member alussa: ", user_team_member_object)
        #user_teamrole = user.get_team_role(id)
        #Team role check
        print("Lomakkeessta saatu team_role_id: ", form.team_role.data)
        
        tr = TeamRole.query.filter_by(id=form.team_role.data).first()
        if tr is None:
            flash('Something went wrong')
            return redirect(url_for('.team_members', id=team.id))
        
        user_team_member_object.team_role_id = form.team_role.data
        print("Lomakkeessta saatu team_role_id: ", form.team_role.data)
        
        db.session.add(user_team_member_object)
        db.session.commit()
        
        tm = TeamMember.query.filter_by(id=user_team_member_object.id).first()
        print("Team member lopussa: ", tm)


        flash("Member permissions updated!")
        return redirect(url_for('.team_members', id=team.id))

    print("team: ", team)
    print("user: ", username)

    return render_template('edit_team.html', title=("Edit {{user.username}}'s team role"), form=form, user=user, team=team, max_role_id = max_role_id)


# @bp.route('/team/<int:id>/edit_member_role/<username>', methods=["GET", "POST"])
# @login_required
# def edit_member_roles(id, username):
#     """ Allows editing member roles """
#     team = Team.query.get_or_404(id)
#     user = User.query.filter_by(username=username).first()
#     form = TeamEditMemberForm()
    

#     if form.validate_on_submit():
#         pass

#     form.
#     return render_template('edit_team.html', title=("Edit your team"), form=form, team=team, user=user)
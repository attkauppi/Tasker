from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory, send_file
from flask_login import current_user, login_required
from application import db, login_manager
from application.main.forms import (
    TaskForm, EditProfileForm, EditProfileAdmin, TeamCreateForm, TeamEditForm,
    TeamInviteForm,
    TeamEditMemberForm,
    EmptyForm,
    TeamTaskForm,
    TeamTaskFormEdit
)#, EmptyForm, PostForm
# from application.main.forms import TestForm
from application.models import (
    User, Task, Role, Team, TeamMember, TeamRole, TeamPermission,
    TeamTask, Board
)
from application.main import bp
from utils.decorators import (
    admin_required,
    permission_required,
    team_moderator_required,
    team_permission_required,
    team_permission_required2,
    team_role_required
)
from sqlalchemy.orm import session
from sqlalchemy import and_, or_, not_, MetaData
meta = MetaData()
from flask import request
from flask import abort
from application.main.forms import TestForm


print("Main luokka")
@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


# def login_required(view):
#     """ Checks if a user is logged in """
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))

#         return view(**kwargs)

#     return wrapped_view

# @bp.before_app_request
# def before_request():
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

#@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
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

@bp.route('/user/<username>/delete', methods=["GET", "POST"])
@login_required
def delete_profile(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        return abort(404)

    form = EmptyForm(value="Delete")

    if form.validate_on_submit():

        db.session.delete(user)
        db.session.commit()
        flash('Your profile was deleted. Hope to see you again sometime!')
        return redirect(url_for('main.index'))
    
    text = """Are you sure you want to do this?
    If you carry this out, you will be removed from all your teams, all your tasks will be removed and none of these will be recoverable."""

    return render_template(
        '_confirm.html',
        username=user.username,
        form=form, value="Delete profile",
        endpoint='main.delete_profile',
        title="Are you sure?",
        text=text
    )


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
#@team_permission_required2(id, TeamPermission.TEAM_OWNER)
@team_moderator_required(id)
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
    
    return render_template('edit_team.html', title=("Edit your team222"), form=form, team=team)    

@bp.route("/teams/<int:id>/delete", methods=["GET", "POST"])
@login_required
@team_permission_required2(id, TeamPermission.TEAM_OWNER)
def team_delete(id):
    team = Team.query.get_or_404(id)
    form = EmptyForm(value="Delete")
    
    if form.validate_on_submit():
        flash('Successfully deleted')

        db.session.delete(team)
        db.session.commit()
        return redirect(url_for('main.index'))

    text = """Are you sure you want to do this?
    If you carry this out, all your team members will be removed, all the tasks they've done or are planning to do will disappear without a trace."""
    return render_template(
        '_confirm.html',
        id=team.id,
        form=form, value="Delete team",
        endpoint='main.team_delete',
        title="Are you sure?",
        text=text
    )

#TODO: Tämä on periaattteessa turha. Halusit yhdennäköistää members-sivun
@bp.route('/teams/<int:id>/invites', methods=["GET", "POST"])
@login_required
def team_invite(id):
    """ Route for sending team invites """
    team = Team.query.get_or_404(id)
    print("Team: ", team)
    users = User.query.all()
    #form = TeamInviteForm()
    form = EmptyForm()

    # Filters out the users already in the team
    us = []
    for i in users:
        if team in i.teams:
            print("Tiimi on jo käyttäjän tiimeissä, ei lisätä")
            #continue
        else:
            us.append(i)
    
    #form = EmptyForm()

    if form.validate_on_submit():
        return redirect(url_for('main.invite_user_to_team', team_id=id, username=form.username.data))
    
    return render_template('team_members.html', team=team, users=us, form=form, team_id=team.id)



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
        return redirect(url_for('main.invite_user_to_team', username=form.username.data, team_id=id))

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

    user = User.query.filter_by(username=username).first_or_404()
    

    args = request.args.to_dict()

    if "team_id" in args:
        print("team id on query parametri")

    team = Team.query.filter_by(id=team_id).first()
   
    d = {
        "team_id": team_id,
        "username": user.username
    }
    
    form = TeamInviteForm()

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
        tm = team.invite_user(user.username)

        # If invite was successful, carry out
        # database operation.
        if tm:
            db.session.add(tm)
            db.session.commit()
        else:
            flash('Did you try to invite someone already in your team?')
            #TODO: Vaihda, jos siirryt toiseen kutsunta menetelmään
            return redirect(url_for('main.invite_to_team', id=team.id))
        
        flash(message=('Invited user ' + user.username))
        print("Suoritus loppumassa iffin sisäiseen redirectiin")
        return redirect(url_for('main.invite_to_team', id=team.id))
    print("Suoritus loppumassa render_templateen")
    #return render_template(url_for('main.invite_to_team', id=team.id))
    return redirect(url_for('main.invite_to_team', id=team.id))


@bp.route('/team/<int:id>', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team(id):
    team = Team.query.get_or_404(id)
    user = current_user
    username = current_user.username

    # print("current_user team_memberships")
    # print(current_user.team_memberships)

    # print("membership tyypit:")
    for i in current_user.team_memberships:
        print("\t", type(i))
    tm = TeamMember.query.filter_by(team_id=id)

    # print("user metodin testaus")
    tm = current_user.get_team_member_object(id)
    # print("user is moderator? ", tm.is_team_moderator())

    # print("current user can moderate?")
    # print(current_user.can_team(id, TeamPermission.CREATE_TASKS))
    if current_user.can_team(id, TeamPermission.CREATE_TASKS):
        print("Kayttaja saa luoda tehtavia!")

    # if current_user.is_team_role(id, "Team member"):
    #     print("Kayttajalla on perus tiimiläisen oikeudet!")
    # #meta.Session.query(Team)

    tm1 = TeamMember.query.filter_by(team_id=id).filter_by(team_member_id=current_user.id).first()

    team_members = team.users
  
    for u in team.users:
        r = u.get_team_role(team.id)
        print("\t rooli: ", r)
        

    return render_template('team.html', team=team, id=team.id, username=username)

@bp.route('/team/<int:id>/members', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team_members(id):
    """ Allows editing member roles """
    team = Team.query.get_or_404(id)

    print("Team users")
    return render_template('team_members.html', team=team, users=team.users)

# TODO: Korjaa team_permission_required-dekoraattori
@bp.route('/team/<int:id>/members/edit/<username>', methods=["GET", "POST"])
@login_required
@team_moderator_required(id)#, TeamPermission.MODERATE_TEAM)
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

    return render_template(
        'edit_team_member.html',
        title=("Edit {{user.username}}'s team role"),
        form=form,
        user=user,
        user_edited=user,
        team=team,
        max_role_id = max_role_id,
        id=team.id,
        username=username
    )

@bp.route('/team/<int:id>/members/edit/<username>/delete', methods=["GET", "POST"])
@login_required
@team_moderator_required(id)
def team_remove_member(id, username):
    """ For removing a member from team """
    team = Team.query.get_or_404(id)
    user = User.query.filter_by(username=username).first()
    
    form = EmptyForm(value="Delete")
    
    if form.validate_on_submit():

        user_team_member_object = user.get_team_member_object(id)
        
        db.session.delete(user_team_member_object)
        db.session.commit()
        flash('Successfully deleted')

        return redirect(url_for('main.team_members', id=team.id))

    text = """Are you sure you want to do this?
    If you carry this out, your team member can't finish the tasks assigned to him/her and they can no longer access the team pages. """
    
    return render_template(
        '_confirm.html',
        id=team.id,
        username=username,
        form=form, value="Remove team member",
        endpoint='main.team_remove_member',
        title="Are you sure?",
        text=text
    )


@bp.route('/teams/<int:id>/tasks', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team_tasks(id):
    """ For team tasks """
    team = Team.query.get_or_404(id)

    #form = Team


    return render_template('team_tasks.html', team=team, team_id=team.id)

@bp.route('/teams/<int:id>/team_tasks/create_task', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def create_team_task(id):
    team = Team.query.get_or_404(id)
    print("saatiin jotain")
    print("Team: ", team.id)

    print("request.endpoint ", request.endpoint)
    form = TeamTaskForm()

    if request.method == "POST":
        
        return redirect(url_for('main.team_tasks_uusi', id=team.id, team=team), code=307)
    # if form.validate_on_submit():
    
    #     t = Task(
    #         title = form.title.data,
    #         description = form.description.data,
    #         #priority = form.description,
    #         done=False,
    #         creator_id=current_user.id,
    #         position="yellow",
    #         priority=False,
    #         board=1,
    #         is_team_task=True
    #     )
    #     db.session.add(t)
    #     db.session.commit()
    #     team_task = team.create_team_task(t)

    #     print("Team task: ", team_task)

    #     #db.session.add(t)
    #     db.session.add(team_task)
    #     db.session.commit()

    #     flash('Created a new task for your team!')
    #     #return redirect(url_for('main.team_tasks_uusi', id=team.id, team=team), code=307)
        
    
    return render_template('_modal.html', id=team.id, form=form, endpoint="main.create_team_task", title="Create task", team=team, teksti="Create task")
    

@bp.route('/teams/<int:id>/team_tasks', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team_tasks_uusi(id):
    team = Team.query.get_or_404(id)
    print("Team: ", team)
    print("Team id: ", team.id)
    args = request.args.to_dict()
    print(request.path)
    print("request.endpoint ", request.endpoint)
    print("args: ", args)

    #print("team.team_tasks")
    #print(team.team_tasks)

    todos = team.get_todo_tasks()
    #print("todos: ", todos)

    doings = team.get_doing_tasks()
    #print("Doings: ", doings)

    dones = team.get_done_tasks()
    #print("Dones: ", dones)

    # team_task = TeamTask.query.filter_by(task_id=task_id).first()
    # print("Team task: ", team_task)
    # assigned_to = None
    #if team_task.doing is not None:   
    

    #print("Assigned to: ", assigned_to)

    form = TeamTaskForm()
    if form.validate_on_submit() and request.method=="POST":
        print("request.args: ", request.args)

        t = Task(
            title = form.title.data,
            description = form.description.data,
            #priority = form.description,
            done=False,
            creator_id=current_user.id,
            position="yellow",
            priority=False,
            board=1,
            is_team_task=True
        )
        db.session.add(t)
        db.session.commit()
        team_task = team.create_team_task(t)

        print("Team task: ", team_task)

        #db.session.add(t)
        db.session.add(team_task)
        db.session.commit()

        flash('Created a new task for your team!')
        # task = Task(
        #     title=form.title.data,
        #     description = form.description.data,
        #     priority = False,#form.priority.data,
        #     creator_id = current_user.id,
        #     is_team_task = True
        # )

        # db.session.add(task)
        # #db.session.flush()
        # db.session.commit()

        # #db.session.flush()
        # task_id = task.id
        # print("Task id: ", task_id)
        # #db.session.commit()

        # task = Task.query.filter_by(id=task_id).first()
        # print("Tietokannan task: ", task)

        # team_task = team.create_team_task(task)
        # print("Team task: ", team_task)
        # db.session.add(team_task)

        # db.session.flush()
        # flash("Created a new task!")

        return render_template('team_tasksU.html', id=team.id, team=team, todos=todos,
        doings=doings,
        dones=dones)
        

    #request = request.args.get('user')
    return render_template(
        'team_tasksU.html',
        id=team.id,
        team=team,
        todos=todos,
        doings=doings,
        dones=dones,
        teksti="Create task")
        #assigned_to=assigned_to)

# @bp.route('/teams/tasks_static', methods=["GET", "POST"])
# @login_required
# def team_tasks():
#     #team = Team.query.get_or_404(id)
#     return send_from_directory('static/js/src/', 'index.html')

@bp.route('/teams/<int:id>/team_tasks/edit_task', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def edit_team_task(id):
    """ Method for editing team tasks """
    #FIXME: tämän modaalissa taisi olla kanssa jotain häikkää?
    task_id = request.args.get('task_id')
    team = Team.query.get_or_404(id)
    task = Task.query.get_or_404(task_id)

    form = TeamTaskFormEdit(team=team, task=task)

    team_task = TeamTask.query.filter_by(task_id=task_id).first()
    
    assigned_to = None
    #if team_task.doing is not None:   
    assigned_to = User.query.filter_by(id=team_task.doing).first()
    form = TeamTaskFormEdit(team=team, task=task)

    print("Task.boards()[DONE]: ", Task.boards()['DONE'])

    #FIXME: Jotain vikaa lomakkeessa täälläkin
    if request.method == "POST":
        task.title = form.title.data
        task.description = form.title.data
        task.board = form.data['board_choices']

        print("samat? ", (int(task.board) == int(Board.DONE)))

        if int(task.board) == int(Board.DONE):
            print("Oli true")
            task.done = True
        elif (int(task.board != int(Board.DONE))):
            task.done = False


        db.session.commit()

        team_task = TeamTask.query.filter_by(task_id=task.id).first()
        team_task = team.create_team_task(task, form_data=form.data)

        db.session.commit()
        
        return redirect(url_for('main.edit_team_task', id=team.id, form=form, title="Edit task", team=team, task=task, assigned_to=assigned_to))
    form.title.data = task.title
    form.description.data = task.description
    return render_template('_modal.html', id=team.id, form=form, endpoint="main.edit_team_task", title="Edit task", team=team, task=task, assigned_to=assigned_to)

@bp.route('/teams/<int:id>/team_tasks/edit_task/<int:task_id>/delete', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team_task_delete(id):
    """ Method for deleting team tasks """



@bp.route('/teams/<int:id>/tasks_frame', methods=["GET", "POST"])
@login_required
def team_tasks_static(id):
    """ For loading static team tasks assets """
    team = Team.query.get_or_404(id)
    #return send_file('templates/_team_tasks2.html')
    return render_template('_team_tasks2.html')

@bp.route('/team/leave2', methods=["GET", "POST"])
@login_required
#@team_role_required(id)
def team_remove_member_self():
    """ For removing a member from team """
    team = Team.query.get_or_404(request.view_args.get('id'))
    print("team: ", team)
    ##team = Team.query.get_or_404(id)
    user = current_user# User.query.filter_by(username=username).first()
    
    form = EmptyForm(value="Delete")
    
    if form.validate_on_submit():

        user_team_member_object = user.get_team_member_object(id)
        
        db.session.delete(user_team_member_object)
        db.session.commit()
        flash('Successfully deleted')

        return redirect(url_for('.index'))

    text = """Are you sure you want to do this?
    If you carry this out, your team member can't finish the tasks assigned to him/her and they can no longer access the team pages. """
    
    return render_template(
        '_confirm.html',
        id=team.id,
        username=current_user.username,
        form=form, value="leave team",
        endpoint='main.team_remove_member_self',
        title="Are you sure?",
        text=text
    )

@bp.route('/team/<int:id>/member/<username>/leave', methods=["GET", "POST"])
@login_required
def team_leave(id, username):
    """ Allows team member to leave team """
    print("request.args: ", request.args)
    print("view args: ", request.view_args)
    team_id = request.view_args.get('id')
    username_arg = request.view_args.get('username')
    team = Team.query.get_or_404(team_id)
    user = User.query.filter_by(username=username_arg).first()
    
    form = EmptyForm(value="Delete")
    # print("User: current_user", user)

    
    #if request.method == "POST":
    #    print("request.args: ", request.args)

    #if form.validate_on_submit():
    if request.method == "POST":

        # print("form.data: ", form.data)
        # print("request.args: ", request.args)
        # print("view args: ", request.view_args)
        if form.validate_on_submit():
            print("Form validated")
            user_team_member_object = user.get_team_member_object(id)
            db.session.delete(user_team_member_object)
            db.session.commit()
            print("request.args: ", request.args)
            print("view args: ", request.view_args)
            flash('Successfully left team')
            return redirect(url_for('main.index'), 307)

        flash('something went wrong')
        return redirect(url_for('main.team', id=team.id), 307)
        
    text = """Are you sure you want to do this?
    If you carry this out, you can't access the team pages nor team tasks again without being invited back and you'll lose your team role """

    return render_template('_confirm.html', id=team.id, username=username, form=form, value="Leave team", endpoint='main.team_leave', title="Are you sure?", text=text)

@bp.route('/send_popup', methods=["GET", "POST"])
@login_required
def user_edit():
    # Testasit tätä
    #user = User.query.filter_by(username=username).first()
    form = TestForm()
    print("Sai jotain")
    form.vastaanottaja.data = "Ari tietenkin"
    form.viesti.data = "Viestin tynka"


    return render_template('_form_edit.html', form=form)


@bp.route('/send/<username>/send', methods=["GET", "POST"])
@login_required
def receive_edit(username):
    form = TestForm()
    user = User.query.filter_by(username=username).first()
    if form.validate_on_submit():
        #vastaanottaja = User.query.filter_by(username=username).first()
        print(form.vastaanottaja.data)
        print(form.viesti.data)
        flash('Mukamas')
        return redirect(url_for('.user', username=user.username), code=307)
    
    flash('Lomake ei validoinut itseään')
    redirect(url_for('.user', username=user.username))










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
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory, send_file
from flask_login import current_user, login_required
from application import db, login_manager
from wtforms import SelectField
from wtforms.form import BaseForm
from application.main.forms import (
    TaskForm, EditProfileForm, EditProfileAdmin, TeamCreateForm, TeamEditForm,
    TeamInviteForm,
    TeamEditMemberForm,
    EmptyForm,
    TeamTaskForm,
    TeamTaskFormEdit,
    MessageForm,
    CommentForm
)#, EmptyForm, PostForm
# from application.main.forms import TestForm
from application.models import (
    User, Task, Role, Team, TeamMember, TeamRole, TeamPermission,
    TeamTask, Board, Message, Notification, Comment
)
import os
from application.main import bp
from utils.decorators import (
    admin_required,
    permission_required,
    team_moderator_required,
    team_permission_required,
    team_permission_required2,
    team_role_required,
    team_task_assigned_or_team_moderator_required
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
    
    if not request.url.startswith('https'):
        return redirect(request.url.replace('http', 'https', 1))
    
    
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

@bp.route('/user/<username>/tasks_dashboard')
@login_required
def tasks_dashboard(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    
    return render_template('tasks_dashboard.html')

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
    
    if user.username != current_user.username:
        return render_template('user.html', user=user, tasks=user_tasks)
    return render_template('user.html', user=user, tasks=user_tasks, form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """ Allows making changes to a user profile """
    form = EditProfileForm(current_user.username)

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

        team_same_names = Team.query.filter_by(title=team.title).all()
        
        for i in team_same_names:
            if current_user.is_team_role(i.id, 'Team owner'):
                flash("You've already created that team ;-)")
                return redirect(url_for('main.team', id=i.id))
                
        db.session.add(team)
        db.session.flush()
        team_id = team.id
        
        db.session.commit()

        # Get the current team's id now that it has
        # been assigned
        t = Team.query.filter_by(id=team_id).first()

        tr = TeamRole.query.filter_by(team_role_name="Team owner").first()

        # Create team_member association table record
        team_member = TeamMember(
            team_id = t.id,
            team_member_id = current_user.id,
            team_role_id = tr.id
        )

        db.session.add(team_member)
        db.session.commit()

        tm_uusi = TeamMember.query.filter_by(team_id=t.id).first()

        flash("Your team was created!")
        return redirect(url_for('main.team', id=t.id))
    
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
    
    return render_template('edit_team.html', id=team.id, title=("Edit your team222"), form=form, team=team)

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


@bp.route('/teams/<int:id>/invites', methods=["GET", "POST"])
@login_required
@team_moderator_required(id)
def team_invite(id):
    """ Route for sending team invites """
    team = Team.query.get_or_404(id)
    users = User.query.all()
    form = EmptyForm()

    # Filters out the users already in the team
    us = []
    for i in users:
        if team in i.teams:
            continue
        else:
            us.append(i)

    if form.validate_on_submit():
        
        username = request.args.get('username')
        user = User.query.filter_by(username=username).first()
        tm = team.invite_user(user.username)

        # If invite was successful, carry out
        # database operation.
        if tm:
            db.session.add(tm)
            db.session.commit()
        else:
            flash('Did you try to invite someone already in your team?')
            return redirect(url_for('main.team_invite', id=team.id, team=team, users=us, form=form, team_id=team.id))
        
        flash(message=('Invited user ' + user.username))
        return redirect(url_for('main.team_invite', id=team.id, team=team, users=us, form=form, team_id=team.id))
        
    return render_template('team_members.html', id=team.id, team=team, users=us, form=form, team_id=team.id)

@bp.route('/team/<int:id>', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team(id):
    team = Team.query.get_or_404(id)
    user = current_user
    username = current_user.username

    tm = TeamMember.query.filter_by(team_id=id)

    tm = current_user.get_team_member_object(id)

    tm1 = TeamMember.query.filter_by(team_id=id).filter_by(team_member_id=current_user.id).first()

    team_members = team.users

    return render_template('team.html', team=team, id=team.id, username=username)

@bp.route('/team/<int:id>/members', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team_members(id):
    """ Allows editing member roles """
    team = Team.query.get_or_404(id)

    print("Team users")
    return render_template('team_members.html', id=team.id, team=team, users=team.users)

@bp.route('/team/<int:id>/members/edit/<username>', methods=["GET", "POST"])
@login_required
@team_moderator_required(id)
def edit_team_member(id, username):
    """ Allows editing a team members team details """
    team = Team.query.get_or_404(id)
    user = User.query.filter_by(username=username).first()

    # Any user should not be able to assign a role higher than
    # they already have to anyone else.
    max_role = current_user.get_team_role(id)

    max_role_id = current_user.get_team_member_object(id).team_role_id

    form = TeamEditMemberForm(max_role_id=max_role_id)

    if form.validate_on_submit():
        user_team_member_object = user.get_team_member_object(id)
        
        tr = TeamRole.query.filter_by(id=form.team_role.data).first()
        if tr is None:
            flash('Something went wrong')
            return redirect(url_for('.team_members', id=team.id))
        
        user_team_member_object.team_role_id = form.team_role.data
        
        db.session.add(user_team_member_object)
        db.session.commit()
        
        tm = TeamMember.query.filter_by(id=user_team_member_object.id).first()
        flash("Member permissions updated!")
        return redirect(url_for('.team_members', id=team.id))

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

    return render_template('team_tasks.html', id=team.id, team=team, team_id=team.id)

@bp.route('/teams/<int:id>/team_tasks/create_task', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def create_team_task(id):
    team = Team.query.get_or_404(id)

    form = TeamTaskForm()
    if form.validate_on_submit() and request.method=="POST":

        t = Task(
            title = form.title.data,
            description = form.description.data,
            done=False,
            creator_id=current_user.id,
            position="yellow",
            priority=False,
            board=1,
            is_team_task=True
        )
        db.session.add(t)
        db.session.flush()
        team_task = team.create_team_task(t)

        db.session.add(team_task)
        db.session.commit()

        flash('Created a new task for your team!')
        return redirect(url_for('main.team_tasks_uusi', id=team.id, team=team), code=307)
    
    return render_template('_modal.html', id=team.id, form=form, endpoint="main.create_team_task", title="Create task", team=team, teksti="Create task")
    

@bp.route('/teams/<int:id>/team_tasks', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team_tasks_uusi(id):
    team = Team.query.get_or_404(id)

    args = request.args.to_dict()
    # Tasks on different boards
    todos = team.get_todo_tasks()
    doings = team.get_doing_tasks()
    dones = team.get_done_tasks()

    return render_template(
        'team_tasksU.html',
        id=team.id,
        team=team,
        todos=todos,
        doings=doings,
        dones=dones,
        teksti="Create task")

@bp.route('/teams/<int:id>/team_tasks/edit_task', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def edit_team_task(id):
    """ Method for editing team tasks """
    #FIXME: tämän modaalissa taisi olla kanssa jotain häikkää?
    task_id = request.args.get('task_id')
    team = Team.query.get_or_404(id)
    task = Task.query.get_or_404(task_id)

    form = TeamTaskFormEdit(team_id=team.id, task=task, user=current_user)

    team_task = TeamTask.query.filter_by(task_id=task_id).first()
    assigned_to = None
    comment_form = CommentForm(task=task, team=team)

    if request.method == "POST":

        # Tällä voisi varmaan tarkistaa, voiko
        # henkilö tehdä muokkauksia tehtävään: 
        # if user.can_team(team.id, TeamPermission.ASSIGN_TASKS):
        if form.validate_on_submit():

            if task.description != form.description.data:
                task.description = form.description.data
            if task.title != form.title.data:
                task.title = form.title.data
            
            if int(task.board) != int(form.data['board_choices']):
                task.board = int(form.data['board_choices'])

                if int(task.board) == int(Board.DONE):
                    task.done = True
                elif (int(task.board != int(Board.DONE))):
                    task.done = False
            form_data = form.data
            team_task = TeamTask.edit_team_task(task, team.id, form_data)

            db.session.commit()

            flash('Saved task changes')
            return redirect(url_for('main.team_tasks_uusi', id=team.id), 307)

    form.title.data = task.title
    form.description.data = task.description
    form.board_choices.default = task.board

    comments = task.comments.order_by(Comment.modified_on.asc())
    
    return render_template(
        '_modal.html',
        id=team.id,
        form=form,
        endpoint="main.edit_team_task",
        title="Edit task",
        team=team,
        task=task,
        task_id=task.id,
        assigned_to=assigned_to,
        board=task.board,
        comments=comments,
        comment_form=comment_form
    )


@bp.route('/teams/<int:id>/team_tasks/<int:task_id>/edit_task/comment', methods=["POST"])
@login_required
@team_role_required(id)
def team_task_comment(id, task_id):
    """ Comenting about tasks - just quickly added,
    not very functional """
    team = Team.query.get_or_404(id)
    task = Task.query.get_or_404(task_id)
    form = CommentForm()

    if request.method == "POST":
        comment = Comment(
            body=form.body.data,
            task=task,
            author=current_user._get_current_object()
        )
        db.session.add(comment)
        db.session.flush()
        db.session.commit()
        flash("Comment added")
        c = {
            'id': comment.id,
            'body': comment.body,
            'body_html': comment.body_html,
            'modified': comment.modified_on,
            'status': 'ok'
        }
        return redirect(url_for('main.team_tasks_uusi', id=team.id))
    
    return redirect(url_for('main.team_tasks_uusi', id=team.id))

@bp.route('/teams/<int:id>/team_tasks/edit_task/<int:task_id>/delete', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team_task_delete(id, task_id):
    """ Method for deleting team tasks """
    team = Team.query.get_or_404(id)
    task = Task.query.filter_by(id=task_id).first()

    if task is None:
        abort(404)

    form = EmptyForm()

    if form.validate_on_submit():
        team_task = TeamTask.query.filter_by(task_id=task.id).first()

        db.session.delete(task)
        db.session.delete(team_task)
        db.session.commit()
        flash('The task was removed!')
        return redirect(url_for('main.team_tasks_uusi', id=team.id))
    
    text = """Are you sure you want to do this?
    If you carry this out, the task and its state will be deleted permanently. """

    return render_template(
        '_confirm.html',
        id=team.id,
        task_id=task.id,
        form=form, value="Delete team task",
        endpoint='main.team_task_delete',
        title="Are you sure?",
        text=text
    )

@bp.route("/teams/<int:id>/task/<int:task_id>/move", methods=["POST"])
@login_required
@team_role_required(id)
def team_task_move(id, task_id):
    """ Moves a team task to the board on the left """
    team = Team.query.get_or_404(id)
    task = Task.query.get_or_404(task_id)

    if request.method == "POST":
        moved = False
        if ("submit_left" in request.form.keys()):
            task_board_orig = task.board
            moved = True
            task.move_left()
            if task.board != task_board_orig:
                db.session.commit()
                flash('Moved left')
            else:
                flash("In the leftmost board already!")
        if ("submit_right" in request.form.keys()):
            task_board_orig = task.board
            task.move_right()
            moved = True

            if task.board != task_board_orig:
                db.session.commit()
                flash('Moved right')
            else:
                flash("In the rightmost board already!")

        if not moved:
            flash("Didn't move for some reason")
        
        return redirect(url_for('main.team_tasks_uusi', id=id))

@bp.route('/team/leave2', methods=["GET", "POST"])
@login_required
@team_role_required(id)
def team_remove_member_self():
    """ For removing a member from team """
    team = Team.query.get_or_404(request.view_args.get('id'))
    user = current_user

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
    team_id = request.view_args.get('id')
    username_arg = request.view_args.get('username')
    team = Team.query.get_or_404(team_id)
    user = User.query.filter_by(username=username_arg).first()
    
    form = EmptyForm(value="Delete")

    if request.method == "POST":

        if form.validate_on_submit():
            user_team_member_object = user.get_team_member_object(id)
            db.session.delete(user_team_member_object)
            db.session.commit()
            flash('Successfully left team')
            return redirect(url_for('main.index'), 307)

        flash('something went wrong')
        return redirect(url_for('main.team', id=team.id), 307)
        
    text = """Are you sure you want to do this?
    If you carry this out, you can't access the team pages nor team tasks again without being invited back and you'll lose your team role """

    return render_template('_confirm.html', id=team.id, username=username, form=form, value="Leave team", endpoint='main.team_leave', title="Are you sure?", text=text)

#### Messages #####
@bp.route("/send_message/<recipient>", methods=["GET", "POST"])
@login_required
def send_message(recipient):
    """ Route for sending messages """
    # TODO: UUsi message-luokka käytössä
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(
            author=current_user,
            recipient=user,
            body=form.message.data
        )
        # Adds a notification of type 'unread_message_count' to
        # receiver, so the variable can be changed in navbar
        user.add_notification('unread_message_count', user.new_messages())
        
        db.session.add(msg)
        db.session.commit()

        flash('Message sent')
        return redirect(url_for('main.user', username=recipient))
    return render_template(
        '_send_message.html',
        title='Send Message',
        form=form,
        recipient=recipient
    )

@bp.route("/messages")
@login_required
def messages():
    """ Method for viewing messages """
    current_user.last_message_read_time = datetime.utcnow()
    # Sets unread_message_notifications number to 0
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    #page = request.args.get('page', 1, type=int)
    
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc())

    #TODO: jos lisää paginoinnin ota tämä mukaan:
            #.paginate(
                #page, current_app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('main.messages', page=messages.next_num) \
    #     if messages.has_next else None
    # prev_url = url_for('main.messages', page=messages.prev_num) \
    #     if messages.has_prev else None
    return render_template('_messages.html', messages=messages)


###----- generic notifications route -------#######
@bp.route("/notifications")
@login_required
def notifications():
    """ Generic route used to retrieve notifications for
    the logged in user 
    
    Returns a JSON payload with a list of notifications for
    the user. Each given as dictionary with 3 elements. Delivered
    in the same order as created, oldest to newest. 
    
    Can be queried since a given time by including the 'since' option.
    Since can be included in the query string of the request URL with
    the UNIX timestamp of the starting time as a floating point number.
    Only notifications, which occurred after this time, will be returned,
    if argument included.
    """
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since
    ).order_by(Notification.timestamp.asc())

    return jsonify(
        [{
                'name': n.name,
                'data': n.get_data(),
                'timestamp': n.timestamp
        } for n in notifications]
    )

@bp.route('/admin/team/<int:id>/get_admin', methods=["POST"])
@login_required
@admin_required
def get_team_admin(id):
    """ Adds admin rights to admin, if moderation
    is needed for some reason """
    team = Team.query.get_or_404(id)
    form = EmptyForm()

    if request.method == "POST":
        tm_admin = team.add_admin_role()
        db.session.add(tm_admin)
        db.session.commit()
        flash('You can now admin this team')
        return redirect(url_for('main.team', id=team.id))

@bp.route("/admin/teams", methods=["GET", "POST"])
@login_required
@admin_required
def admin_teams():
    teams = Team.query.all()

    return render_template('_teams.html', teams=teams)

@bp.route("/admin/users", methods=["GET", "POST"])
@login_required
@admin_required
def admin_users():
    users = User.query.all()

    return render_template('users.html', users=users)

@bp.route('/teams/<int:id>/edit_team_admin', methods=["GET", "POST"])
@login_required
@admin_required
def edit_team_admin(id):
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
    
    return render_template('edit_team.html', id=team.id, title=("Edit your team222"), form=form, team=team)    

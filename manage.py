from flask.cli import FlaskGroup

from application import create_app, db
from application.models import User, Task, Team, TeamMember, TeamPermission,TeamRole, TeamTask, Role, Messages, Message, Notification

app = create_app()

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    u = User(username='testi', email='kauppi.ari@gmail.com', confirmed=True)
    u.set_password('testi')
    db.session.add(u)
    db.session.commit()

if __name__ == '__main__':
    cli()
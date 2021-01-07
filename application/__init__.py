from flask import Flask, request, current_app, jsonify
import logging
from flask import redirect, render_template, request, session
import os
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask_migrate import Migrate
from flask_restful import Api
#from application.api import AuthAPI
# Globally accessible libraries
# Lahde: https://hackersandslackers.com/flask-application-factory/

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
api = Api()


def create_app(config_class=Config):
    """ Initializes the core application """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)
    # app.config.from_object('config.DevConfig')
    #app.config.from_object(os.environ['APP_SETTINGS'])
    print(os.environ.get('SECRET_KEY'))
    app.config['DEBUG'] = True
    app.debug = True
    # Tämä toimii

    # app.config.from_object(os.environ.get('APP_SETTINGS'))

    #app.config.from_object('config.DevConfig')

    #app = Flask(__name__, instance_relative_config=False)
    #app.config.from_object(os.environ['APP_SETTINGS'])

    #app.config.from_object('config.Config')
    
    #app.config['DEBUG'] = True
    #app.debug = True
    # Vaikutti mielekkäältä opetella käyttämään application factory -juttuja
    # suunnilleen jo tässä vaiheessa, jotta refaktorointia ei synny niin
    # valtavasti. Vinkkeinä käytin mm. seuraavaa
    # Lahde: https://hackersandslackers.com/flask-application-factory/
    
    #TODO: Utilizing databases is actually still not implemented.
    # Initialize plugins
    # from . import db


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)

    # if app.config['SSL_REDIRECT']:
    #     from flask_sslify import SSLify
    #     sllify = SSLify(app)

    if os.environ.get('DYNO'):
        app.config['SERVER_NAME'] = "https://tsohatasker.herokuapp.com/"


    from application.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from application.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from application.main import bp as main_bp
    app.register_blueprint(main_bp)
    #FIXME Tämä voi aiheuttaa 
    from application.api import bp as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api_blueprint/v1')

    # Esimerkki: https://stackoverflow.com/questions/60549530/pytest-assertionerror-view-function-mapping-is-overwriting-an-existing-endpoin
    
    from application.api import get_blueprint

    api_bp_restful = get_blueprint()
    api = Api(api_bp_restful)

    # from application.api import api_bp_restful
    # api = Api(api_bp_restful)

    

    from application.api.resources import AuthAPI, TaskListAPI, TaskCheckAPI, TaskAPI
    api.add_resource(AuthAPI, '/auth/tokens', endpoint='tokens')
    api.add_resource(TaskListAPI, '/tasks', endpoint='tasks')
    api.add_resource(TaskCheckAPI, '/task_check/<int:id>', endpoint='task_check')
    api.add_resource(TaskAPI, '/task/<int:id>', endpoint='task')
    # api.add_resource(AuthAPI, '/api/v1/tokens', endpoint='tokens')
    # api.add_resource(TaskListAPI, '/api/v1/tasks', endpoint='tasks')
    # api.add_resource(TaskCheckAPI, '/api/v1/task_check/<int:id>', endpoint='task_check')
    # api.add_resource(TaskAPI, '/api/v1/task/<int:id>', endpoint='task')

    app.register_blueprint(api_bp_restful, url_prefix="/api/v1")

    # api.add_resource(AuthAPI, '/tokens', endpoint='tokens')
    # api.add_resource(TaskListAPI, '/tasks', endpoint='tasks')
    # api.add_resource(TaskCheckAPI, '/task_check/<int:id>', endpoint='task_check')
    # api.add_resource(TaskAPI, '/task/<int:id>', endpoint='task')
    
    # app.register_blueprint(api_bp_restful)





    # api.app = app
    # api.init_app(app)
    # api.add_resource(AuthAPI, '/api/v1/tokens', endpoint='tokens')


    #api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint='task')









    # if app.config['MAIL_SERVER']:
    #     auth = None
    #     if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
    #         print("oli username tai salasana")
    #         auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    #     secure = None
    #     if app.config['MAIL_USE_SSL']:
    #         secure = ()
    #     mail_handler = SMTPHandler(
    #         mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
    #         fromaddr = 'tasker.info.noreply@' + app.config['MAIL_SERVER'],
    #         toaddrs = app.config['ADMINS'],
    #         subject="Tasker ongelma",
    #         credentials=auth,
    #         secure=secure
    #     )
    #     mail_handler.setLevel(logging.ERROR)
        # app.logger.addHandler(mail_handler)
        # if not os.path.exists('logs'):
        #     os.mkdir('logs')
        # file_handler = RotatingFileHandler('logs/microblog.log',
        #                                    maxBytes=10240, backupCount=10)
        # file_handler.setFormatter(logging.Formatter(
        #     '%(asctime)s %(levelname)s: %(message)s '
        #     '[in %(pathname)s:%(lineno)d]'))
        # file_handler.setLevel(logging.INFO)
        # app.logger.addHandler(file_handler)

        # app.logger.setLevel(logging.INFO)
        # app.logger.info('Microblog startup')


        
    
    #if not app.testing:
    #    if app.config['MAIL_SERVER']:
    #        print("Mail server oli")

    
    #
    
    with app.app_context():
        #db.create_all()
        #from .db import init_db, init_db_command
        #init_db()
        #init_db()

        from application import models
        
        db.create_all()
        from application.models import Role
        Role.insert_roles()

        from application.models import TeamRole
        TeamRole.insert_roles()

        from application.models import Task
        Task.insert_boards()
        #_db.init_db()
        #db.create_all()
    #     @app.route("/send")
    #     def index():
    #         msg = Message('Hello', sender = 'tasker.info.noreply@gmail.com', recipients = ['kauppi.ari@gmail.com'])
    #         msg.body = "Hello Flask message sent from Flask-Mail"
    #         mail.send(msg)
    #         return "Sent"
        
    #     mail_settings = {
    #         "MAIL_SERVER": 'smtp.gmail.com',
    #         "MAIL_PORT": 465,
    #         "MAIL_USE_TLS": False,
    #         "MAIL_USE_SSL": True,
    #         "MAIL_USERNAME": "",
    #         "MAIL_PASSWORD": ""
    #     }
    #     app.config.update(mail_settings)
        
    #     mail.connect()
    #     with mail.record_messages() as outbox:
    #         msg = Message("Subject",sender="tasker@...",recipients=['vastaanottaja@sahkoposti'])
    #         msg.body = "test email"
            
    #         mail.send(msg)
    #     print(mail.ConnectionError)
    #     print(msg)
    #     print(mail.record_messages)
        

    #     app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    #     app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
    #     app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    #     app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    #     app.config['MAIL_USE_TLS'] = True

    #     @app.route('/crash')
    #     def main():
    #         raise Exception()
        
    #     app.register_blueprint(errors_bp)
    #     app.register_blueprint(auth_bp, url_perfix='/auth')
    #     app.register_blueprint(main_bp)

        # Creates database tables
        

        # Register blueprints
        # See https://hackersandslackers.com/flask-application-factory/

        #from . import auth
        #app.register_blueprint(auth.bp)
        # @app.route("/send_email", methods=["GET", "POST"])
        # def send():

        #     msg = Message(subject="Hello", sender=app.config.get('MAIL_USERNAME'), recipients=['kauppi.ari@gmail.com'], body="Sent an email")
        #     mail.send(msg)
        #     return jsonify("Email sent")

        # @app.route("/", methods=["GET", "POST"])
        # def index():
        #     result = db.session.execute("SELECT COUNT(*) FROM messages")
        #     count = result.fetchone()[0]
        #     result = db.session.execute("SELECT content FROM messages")
        #     messages = result.fetchall()

        #     user_agent = request.headers.get('User-Agent')
        #     return render_template("index.html", count=count, messages=messages,user_agent=user_agent)
        
        # @app.route("/send", methods=["POST"])
        # def send():
        #     content = request.form["content"]
        #     sql = "INSERT INTO messages (content) VALUES (:content)"
        #     db.session.execute(sql, {"content":content})
        #     db.session.commit()
        #     return redirect("/")
    return app

from application import models



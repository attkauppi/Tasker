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
    app.config.from_object('config.DevConfig')
    app.config['DEBUG'] = True
    app.debug = True
    # Tämä toimii

    #if os.environ.get('DYNO'):
    #    app.config.from_object('config.HerokuConfig')
    # if app.config['SSL_REDIRECT']:
    #     from flask_sslify import SSLify
    #     sllify = SSLify(app)

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

    #if os.environ.get('DYNO'):
    #    app.config['SERVER_NAME'] = 'example.com'


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

    from application.api.resources import AuthAPI, TaskListAPI, TaskCheckAPI, TaskAPI
    api.add_resource(AuthAPI, '/auth/tokens', endpoint='tokens')
    api.add_resource(TaskListAPI, '/tasks', endpoint='tasks')
    api.add_resource(TaskCheckAPI, '/task_check/<int:id>', endpoint='task_check')
    api.add_resource(TaskAPI, '/task/<int:id>', endpoint='task')
  
    app.register_blueprint(api_bp_restful, url_prefix="/api/v1")

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
       

        # Register blueprints
        # See https://hackersandslackers.com/flask-application-factory/

    return app

from application import models



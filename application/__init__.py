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
# Globally accessible libraries
# Lahde: https://hackersandslackers.com/flask-application-factory/
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()

def create_app():
    """ Initializes the core application """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(os.environ['APP_SETTINGS'])
    print(os.environ.get('SECRET_KEY'))
    app.config['DEBUG'] = True
    app.debug = True

    #app = Flask(__name__, instance_relative_config=False)
    #app.config.from_object(os.environ['APP_SETTINGS'])
    #app.config.from_object('config.Config')
    app.config.from_object('config.DevConfig')
    #app.config['DEBUG'] = True
    #app.debug = True
    
    # Vaikutti mielekkäältä opetella käyttämään application factory -juttuja
    # suunnilleen jo tässä vaiheessa, jotta refaktorointia ei synny niin
    # valtavasti. Vinkkeinä käytin mm. seuraavaa
    # Lahde: https://hackersandslackers.com/flask-application-factory/
    
    #TODO: Utilizing databases is actually still not implemented.
    # Initialize plugins
    # from . import db
    
    mail_settings = {
        "MAIL_SERVER": 'smtp.gmail.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": 'tasker.info.noreply@gmail.com',
        "MAIL_PASSWORD": 'pvXR32X2'
    }
    app.config.update(mail_settings)
    mail.init_app(app)
    from application import models#import Messages,User
    # from . import db
    from application.models import Messages, User
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    from application.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from application.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from application.main import bp as main_bp
    app.register_blueprint(main_bp)

    
    with app.app_context():
        #from .db import init_db
        #init_db()
        #_db.init_db()
        db.create_all()
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

        #     msg = Message(subject="Hello", sender=app.config.get('MAIL_USERNAME'), recipients=['vastaanottaja@sahkoposti'], body="Sent an email")
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
    
        # @app.route("/new")
        # def new():
        #     return render_template("new.html")
        
        # @app.route("/send", methods=["POST"])
        # def send():
        #     content = request.form["content"]
        #     sql = "INSERT INTO messages (content) VALUES (:content)"
        #     db.session.execute(sql, {"content":content})
        #     db.session.commit()
        #     return redirect("/")
    return app

from application import models


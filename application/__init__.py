from flask import Flask
from flask import redirect, render_template, request, session
import os
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager

# Globally accessible libraries
# Lahde: https://hackersandslackers.com/flask-application-factory/
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """ Initializes the core application """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(os.environ['APP_SETTINGS'])
    # app.config.from_object('config.Config')
    # app.config.from_object('config.DevConfig')
    # app.config['DEBUG'] = True
    
    # Vaikutti mielekkäältä opetella käyttämään application factory -juttuja
    # suunnilleen jo tässä vaiheessa, jotta refaktorointia ei synny niin
    # valtavasti. Vinkkeinä käytin mm. seuraavaa
    # Lahde: https://hackersandslackers.com/flask-application-factory/
    
    #TODO: Utilizing databases is actually still not implemented.
    # Initialize plugins
    from . import db
    from application.models import Messages
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # Include routes
        from . import routes

        # Creates database tables
        db.create_all()

        # Register blueprints
        # See https://hackersandslackers.com/flask-application-factory/

        from . import auth
        app.register_blueprint(auth.bp)
        

        @app.route("/", methods=["GET", "POST"])
        def index():
            result = db.session.execute("SELECT COUNT(*) FROM messages")
            count = result.fetchone()[0]
            result = db.session.execute("SELECT content FROM messages")
            messages = result.fetchall()

            user_agent = request.headers.get('User-Agent')
            return render_template("index.html", count=count, messages=messages,user_agent=user_agent)
        
        @app.route("/new")
        def new():
            return render_template("new.html")
        
        @app.route("/send", methods=["POST"])
        def send():
            content = request.form["content"]
            sql = "INSERT INTO messages (content) VALUES (:content)"
            db.session.execute(sql, {"content":content})
            db.session.commit()
            return redirect("/")

        return app




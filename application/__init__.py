from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Globally accessible libraries
db = SQLAlchemy()

def create_app():
    """ Initializes the core application """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    # app.config.from_object('config.DevConfig')
    # app.config['DEBUG'] = True
    
    # Vaikutti mielekkäältä opetella käyttämään application factory -juttuja
    # suunnilleen jo tässä vaiheessa, jotta refaktorointia ei synny niin
    # valtavasti. Vinkkeinä käytin mm. seuraavaa
    # Lahde: https://hackersandslackers.com/flask-application-factory/
    
    #TODO: Utilizing databases is actually still not implemented.
    # Initialize plugins
    db.init_app(app)

    with app.app_context():
        # Include routes
        from . import routes

        # Register blueprints
        # See https://hackersandslackers.com/flask-application-factory/

        @app.route("/", methods=["GET", "POST"])
        def index():
            return "No toimisitkohan jo. Ja päivää päivää!"

        return app




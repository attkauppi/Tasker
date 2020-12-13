
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import click
from flask import current_app, g
from flask.cli import with_appcontext
import os

db = SQLAlchemy()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            current_app.config['SQLALCHEMY_DATABASE_URI')
        )
    return g.db


def init_db():
    db = get_db()
    # Vanha tapa
    #with current_app.open_resource('schema.sql') as f:
    #    db.executescript(f.read().decode('utf8'))
    #with db as cursor:
    #    cursor.execute(open('schema.sql', 'r').read())
    #with current_app.open_resource('schema.sql') as :
    #    db.executescript(f.read().decode('utf8'))

    conn = psycopg2.connect(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = conn.cursor()
    #with conn:
    #    cursor.execute(open('schema.sql', 'r').read())
    with current_app.open_resource('schema.sql') as f:
        cursor.execute(f.read().decode('utf8'))


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


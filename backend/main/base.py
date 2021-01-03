import os
import click

from flask import current_app, g
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main.__init__ import app_instance_path

engine = create_engine('sqlite:///' + os.path.join(app_instance_path, 'db.sqlite3'))
Session = sessionmaker(bind=engine)

Base = declarative_base()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def init_db():
    Base.metadata.create_all(engine)

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')
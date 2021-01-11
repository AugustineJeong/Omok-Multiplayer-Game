import os
import click

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from main.__init__ import app_instance_path

engine = create_engine('sqlite:///' + os.path.join(app_instance_path, 'db.sqlite3'))
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()

def init_app(app):
    app.cli.add_command(init_db_command)

def init_db():
    from main.user import User
    Base.metadata.create_all(engine)

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')
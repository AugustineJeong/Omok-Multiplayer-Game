# The following license applies to SQLAlchemy
# Copyright (c) 2005-2021 Michael Bayer and contributors. SQLAlchemy is a trademark of Michael Bayer.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Other code in file written by Augustine Jeong
# Copyright (c) 2021 Augustine Jeong

import os
import click

from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    wins = Column(Integer)
    losses = Column(Integer)
    level = Column(Integer)

    def __init__(self, username, password, wins=0, losses=0, level=1):
        self.username = username
        self.password = password
        self.wins = wins
        self.losses = losses
        self.level = level

def init_app(app):
    app.cli.add_command(init_db_command)

def init_db():
    Base.metadata.create_all(engine)

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Successfully initialized the database.')
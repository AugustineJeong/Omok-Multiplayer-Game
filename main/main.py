# The following license applies to Flask
# Some of the code on this file have been based off of Flask's documentation.
# Copyright 2010 Pallets
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The following license applies to SQLAlchemy
# Copyright (c) 2005-2021 Michael Bayer and contributors. SQLAlchemy is a trademark of Michael Bayer.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# The following license applies to Flask-SocketIO
# The MIT License (MIT)
# Copyright (c) 2014 Miguel Grinberg
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# The following license applies to werkzeug
# Copyright 2007 Pallets
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2 .Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Other code in file written by Augustine Jeong
# Copyright (c) 2021 Augustine Jeong

import os
import click

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from sqlalchemy import create_engine, Column, String, Integer, Date
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import check_password_hash, generate_password_hash
from collections import deque

# ------------------------------------------------------------------------------------------
# Flask app, SocketIO, and SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
	SECRET_KEY ='dev',
)

try:
	os.makedirs(app.instance_path)
except OSError:
	pass

engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'db.sqlite3'))
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

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

init_app(app)

socketIO = SocketIO(app)

# ------------------------------------------------------------------------------------------
# authentication

@app.route('/auth/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':           
		databaseSession = Session()

		username = request.form['username']
		password = request.form['password']
		confirm_password = request.form['confirm_password']

		error = None

		if not username:
			error = 'Username is required.'
		elif not password:
			error = 'Password is required.'
		elif len(username) > 10:
			error = 'Username should be under 10 characters.'
		elif len(password) > 15:
			error = 'Password should be under 15 characters.'
		elif username.isspace():
			error = 'Username cannot be empty.'
		else: 
			userExists = None
			try:
				userExists = (databaseSession.query(User).filter(User.username == username).first())
			except: 
				pass
			if (userExists is not None):
				error = 'Username \'{}\' already exists.'.format(username)
			elif password != confirm_password:
				error = 'Passwords do not match.'
			
		if error is None:
			databaseSession.add(User(username, generate_password_hash(password)))
			databaseSession.commit()
			databaseSession.close()
			return redirect(url_for('login'))
		else:
			databaseSession.commit()
			databaseSession.close()
			flash(error)

	if (g.user is not None):
		return redirect(url_for('main_home'))
	else:
		return render_template('auth/register.html')

@app.route('/auth/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		if request.form['sign_in_screen_button'] == 'sign_up':
			return redirect(url_for('register'))
		elif request.form['sign_in_screen_button'] == 'sign_in':
			databaseSession = Session()

			username = request.form['username']
			password = request.form['password']

			user = None
			try:
				user = databaseSession.query(User).filter(User.username==username).first()
			except:
				pass

			error = None

			if not username:
				error = 'Username is required.'
			elif not password:
				error = 'Password is required.'
			elif (user is None):
				error = 'Incorrect username or password.'
			elif not check_password_hash(user.password, password):
				error = 'Incorrect username or password.'

			databaseSession.close()

			if error is None:
				session.clear()
				session['user_id'] = user.id
				return redirect(url_for('main_home'))

			flash(error)

	if (g.user is not None):
		return redirect(url_for('main_home'))
	else:
		return render_template('auth/login.html')

@app.route('/auth/logout')
def logout():
	session.clear()
	return redirect(url_for('main_home'))

@app.before_request
def load_logged_in_user():
	user_id = session.get('user_id')
	if user_id is None:
		g.user = None
	else:
		databaseSession = Session()
		try:
			g.user = databaseSession.query(User).filter(User.id==user_id).first()
		except:
			pass
		databaseSession.close()

def login_required():
	if g.user is None:
		return redirect(url_for('login'))
	else:
		return None

# ------------------------------------------------------------------------------------------
# index

playersInGame = set()

@app.route('/index', methods=('GET', 'POST'))
def main_home():
	if request.method == 'POST':
		if 'corner_button' in request.form:
			if request.form['corner_button'] == 'sign_in':
				return redirect(url_for('login'))

			elif request.form['corner_button'] == 'log_out':
				return redirect(url_for('logout'))
				
		elif 'play_button' in request.form:
			if request.form['play_button'] == 'start_game':
				return redirect(url_for('game'))

	if (g.user is None):
		return render_template('index.html', is_signed_in = 0)
	else:
		user_info = (g.user.username + " / Wins: " + str(g.user.wins) + " / Losses: " + str(g.user.losses)
		+ " / Level: " + str(g.user.level))
		return render_template('index.html', is_signed_in = 1, user_info = user_info)

@app.route('/index/game', methods=('GET', 'POST'))
def game():
	if request.method == 'POST':
		if 'corner_button' in request.form:
			if request.form['corner_button'] == 'exit_queue':
				return redirect(url_for('main_home'))

	return_value = login_required()
	if return_value is not None:
		return return_value

	# do not let player join new game session if player is already in one
	if g.user.id in playersInGame:
		return redirect(url_for('main_home'))

	playersInGame.add(g.user.id)

	return render_template('game.html')

@app.route('/index/finding', methods=['GET'])
def finding_game():
	return_value = login_required()
	if return_value is not None:
		return return_value

	return render_template('finding.html')

game_rooms_dictionary = dict()
sid_dictionary = dict()
game_rooms = list()
for i in range(10):
	game_rooms.append(list())
connectedPlayersList = deque()

# TODO: Implement a way to detect when the user is disconnected and re-implement the below function

# @socketIO.on('disconnect')
# def handle_disconnect_event():
#     try:
#         leave_room(room_number)
#         room_number = game_rooms_dictionary.pop('key', session.get('user_id'))
#         game_rooms[room_number].remove(session.get('user_id'))
#         connectedPlayersList.remove(session.get('user_id'))

#         app.logger.info("removing user_id: " + session.get('user_id'))
#     except:
#         pass

@socketIO.on('request_room')
def request_game_room():
	if session.get('user_id') not in connectedPlayersList:
		connectedPlayersList.append(session.get('user_id'))
		for i in range(10):
			if 2 > len(game_rooms[i]):
				app.logger.info("# of players currently in room " + str(i) + " is (before adding): " + str(len(game_rooms[i])))
				game_rooms[i].append(session.get('user_id'))
				join_room(i)
				app.logger.info("Player " + str(session.get('user_id')) + " joined room number: " + str(i))
				game_rooms_dictionary[session.get('user_id')] = i
				sid_dictionary[session.get('user_id')] = request.sid
				app.logger.info("# of players currently in room " + str(i) + " is (after adding): " + str(len(game_rooms[i])))
				break

def notifyCurrentSessionPlayerColour():
	isPlayerBlue = None
	i = game_rooms_dictionary[session.get('user_id')]
	for player in game_rooms[i]:
		try:
			isPlayerBlue = game_rooms[i].index(player)
			app.logger.info("player " + str(player) + " colour is: " + str(isPlayerBlue))
		except:
			pass
		if isPlayerBlue == 0 or isPlayerBlue == 1:
			socketIO.emit('player_colour_assignment', {'isPlayerBlue': isPlayerBlue}, room=sid_dictionary[player])

@socketIO.on('check_entered_room')
def check_entered_game_room():
	try:
		if len(game_rooms[game_rooms_dictionary[session.get('user_id')]]) == 2:
			socketIO.emit('check_entered_room_response', {'response': True}, room=game_rooms_dictionary[session.get('user_id')])
			i = game_rooms_dictionary[session.get('user_id')]
			app.logger.info("player " + str(game_rooms[i][0]) + " and " + str(game_rooms[i][1]) + " in room")
			notifyCurrentSessionPlayerColour()
		else:
			socketIO.emit('check_entered_room_response', {'response': False}, room=game_rooms_dictionary[session.get('user_id')])
			i = game_rooms_dictionary[session.get('user_id')]
			app.logger.info("player " + str(game_rooms[i][0]) + " and " + str(game_rooms[i][1]) + " not in room")
	except:
		app.logger.error("could not find current game room number")
		json = {'response': False}
		socketIO.emit('check_entered_room_response', json, room=game_rooms_dictionary[session.get('user_id')])

@socketIO.on('disconnect_from_room')
def disconnect_from_game_room():
	load_logged_in_user()
	playersInGame.remove(g.user.id)

	try:
		if session.get('user_id') in connectedPlayersList:
			connectedPlayersList.remove(session.get('user_id'))
			i = game_rooms_dictionary[session.get('user_id')]
			app.logger.info("# of players currently in room " + str(i) + " is (before removing): " + str(len(game_rooms[i])))
			leave_room(i)
			game_rooms[i].remove(session.get('user_id'))
			del game_rooms_dictionary[session.get('user_id')]
			app.logger.info("Player " + str(session.get('user_id')) + " left room number: " + str(i))
			app.logger.info("# of players currently in room " + str(i) + " is (after removing): " + str(len(game_rooms[i])))
	except:
		app.logger.error("error disconnecting user from game room")
		pass

@socketIO.on('stone_placement')
def handle_my_custom_event(json):
	socketIO.emit('placement_response', json, room=game_rooms_dictionary[session.get('user_id')])

# ------------------------------------------------------------------------------------------
# run app

if __name__ == '__main__':
	socketIO.run(app)
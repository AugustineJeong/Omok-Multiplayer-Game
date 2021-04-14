# The following license applies to Flask
# Some of the code on this file have been based off of Flask's documentation.
# Copyright 2010 Pallets
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import check_password_hash, generate_password_hash
from collections import deque

# ------------------------------------------------------------------------------------------
# Flask app, SocketIO

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
	SECRET_KEY ='dev',
)

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
# index

@app.route('/', methods=('GET', 'POST'))
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
				
	return render_template('index.html')

@app.route('/game', methods=('GET', 'POST'))
def game():
	if request.method == 'POST':
		if 'corner_button' in request.form:
			if request.form['corner_button'] == 'exit_queue':
				return redirect(url_for('main_home'))

	return render_template('game.html')

game_rooms_dictionary = dict()
game_rooms = list()
for i in range(25):
	game_rooms.append(list())
connectedPlayersList = deque()

@socketIO.on('request_room')
def request_game_room():
	if request.sid not in connectedPlayersList:
		connectedPlayersList.append(request.sid)
		for i in range(10):
			if 2 > len(game_rooms[i]):
				app.logger.info("# of players currently in room " + str(i) + " is (before adding): " + str(len(game_rooms[i])))
				game_rooms[i].append(request.sid)
				join_room(i)
				app.logger.info("Player " + str(request.sid) + " joined room number: " + str(i))
				game_rooms_dictionary[request.sid] = i
				app.logger.info("# of players currently in room " + str(i) + " is (after adding): " + str(len(game_rooms[i])))
				break

def notifyCurrentSessionPlayerColour():
	isPlayerBlue = None
	i = game_rooms_dictionary[request.sid]
	for player in game_rooms[i]:
		try:
			isPlayerBlue = game_rooms[i].index(player)
			app.logger.info("player " + str(player) + " colour is: " + str(isPlayerBlue))
		except:
			pass
		if isPlayerBlue == 0 or isPlayerBlue == 1:
			socketIO.emit('player_colour_assignment', {'isPlayerBlue': isPlayerBlue}, room=player)

@socketIO.on('check_entered_room')
def check_entered_game_room():
	try:
		if len(game_rooms[game_rooms_dictionary[request.sid]]) == 2:
			socketIO.emit('check_entered_room_response', {'response': True, 'game_room_number': (game_rooms_dictionary[request.sid] + 1)}, 
				room=game_rooms_dictionary[request.sid])
			i = game_rooms_dictionary[request.sid]
			app.logger.info("player " + str(game_rooms[i][0]) + " and " + str(game_rooms[i][1]) + " in room")
			notifyCurrentSessionPlayerColour()
		else:
			socketIO.emit('check_entered_room_response', {'response': False}, room=game_rooms_dictionary[request.sid])
			i = game_rooms_dictionary[request.sid]
			app.logger.info("player " + str(game_rooms[i][0]) + " and " + str(game_rooms[i][1]) + " not in room")
	except:
		app.logger.error("could not find current game room number")
		socketIO.emit('check_entered_room_response', {'response': False}, room=game_rooms_dictionary[request.sid])

@socketIO.on('disconnect_from_room')
def disconnect_from_game_room():
	try:
		if request.sid in connectedPlayersList:
			socketIO.emit('game_session_valid_response', {'session_valid': False}, room=game_rooms_dictionary[request.sid])
			connectedPlayersList.remove(request.sid)
			i = game_rooms_dictionary[request.sid]
			app.logger.info("# of players currently in room " + str(i) + " is (before removing): " + str(len(game_rooms[i])))
			leave_room(i)
			game_rooms[i].remove(request.sid)
			del game_rooms_dictionary[request.sid]
			app.logger.info("Player " + str(request.sid) + " left room number: " + str(i))
			app.logger.info("# of players currently in room " + str(i) + " is (after removing): " + str(len(game_rooms[i])))
	except:
		app.logger.error("error disconnecting user from game room")
		pass

@socketIO.on('stone_placement')
def stone_placement(json):
	socketIO.emit('placement_response', json, room=game_rooms_dictionary[request.sid])

# ------------------------------------------------------------------------------------------
# run app

if __name__ == '__main__':
	socketIO.run(app)
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

# Other code in file written by Augustine Jeong
# Copyright (c) 2021 Augustine Jeong

import os
import click
import time
import random
import json

from flask import Flask, flash, g, redirect, render_template, request, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect, close_room
from collections import deque

# ------------------------------------------------------------------------------------------
# Flask app, SocketIO

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
	SECRET_KEY ='dev'
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
# random games SocketIO

game_rooms_dictionary = dict()
game_rooms = list()
for i in range(50):
	game_rooms.append(list())
connectedPlayersList = deque()

# handler for the room request from player in random games page
@socketIO.on('request_room')
def request_game_room():
	app.logger.info("Player " + str(request.sid) + " requested room")
	if request.sid not in connectedPlayersList:
		connectedPlayersList.append(request.sid)
		for i in range(len(game_rooms)):
			if 2 > len(game_rooms[i]):
				app.logger.info("# of players currently in room " + str(i + 1) + " is (before adding): " + str(len(game_rooms[i])))
				game_rooms[i].append(request.sid)
				join_room(i)
				app.logger.info("Player " + str(request.sid) + " joined room number: " + str(i + 1))
				game_rooms_dictionary[request.sid] = i
				app.logger.info("# of players currently in room " + str(i + 1) + " is (after adding): " + str(len(game_rooms[i])))
				break


# notify the two players in the room of their colour (blue [1] or grey [0])
def notifyCurrentSessionPlayerColour():
	isPlayerBlue = None
	i = game_rooms_dictionary[request.sid]
	for sid in game_rooms[i]:
		try:
			isPlayerBlue = game_rooms[i].index(sid)
			app.logger.info("player " + str(sid) + " colour is: " + str(isPlayerBlue))
		except:
			pass
		if isPlayerBlue == 0 or isPlayerBlue == 1:
			socketIO.emit('player_colour_assignment', {'isPlayerBlue': isPlayerBlue}, room=sid)


# alert the users in random games page if they have been placed in a room yet or not
@socketIO.on('check_entered_room')
def check_entered_game_room():
	app.logger.info("Player " + str(request.sid) + " is requesting check_entered_room")
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


# handler for user disconnection, triggered when one of the players closes their page (may not work for some browsers)
@socketIO.on('disconnect_from_room')
def disconnect_from_game_room():
	try:
		if request.sid in connectedPlayersList:
			socketIO.emit('game_session_valid_response', {'session_valid': False}, room=game_rooms_dictionary[request.sid])
			i = game_rooms_dictionary[request.sid]	

			# sleep to allow socketIO emit to reach client before disconnecting client
			time.sleep(2)

			app.logger.info("clearing room " + str(i + 1))	
			
			for sid in game_rooms[i]:
				del game_rooms_dictionary[sid]
				disconnect(sid)
				connectedPlayersList.remove(sid)
			
			close_room(i)
			game_rooms[i].clear()
			app.logger.info("# of players currently in room " + str(i + 1) + " is (after removing): " + str(len(game_rooms[i])))
	except:
		app.logger.error("error disconnecting user from game room, perhaps user has already been disconnected")


# emits stone placements of the players to their room
@socketIO.on('stone_placement')
def stone_placement(json):
	socketIO.emit('placement_response', json, room=game_rooms_dictionary[request.sid])

# ------------------------------------------------------------------------------------------
# private game rooms SocketIO

sid_private_game_rooms_dictionary = dict()
private_game_rooms_dictionary = dict()
private_room_connected_players = set()

unique_name_list = ['dolphin', 'donguri', 'turtle', 'omok', 'orange', 'monkey', 'cactus', 'game']

# generates a unique room code for private game rooms
def get_unique_room_code():
	random_code = unique_name_list[random.randint(0, 7)]
	random_code += str(random.randint(0, 100000))
	if random_code not in sid_private_game_rooms_dictionary.keys():
		return random_code
	else:
		return get_unique_room_code()


# handler for user disconnection, triggered when one of the players closes their page (may not work for some browsers)
@socketIO.on('disconnect_from_private_room')
def disconnect_from_private_game_room():
	try:
		if request.sid in private_room_connected_players:
			socketIO.emit('game_session_valid_response_private_room', {'session_valid': False}, 
				room=sid_private_game_rooms_dictionary[request.sid])
			private_room_name = sid_private_game_rooms_dictionary[request.sid]	

			# sleep to allow socketIO emit to reach client before disconnecting client
			time.sleep(2)

			app.logger.info("clearing room " + private_room_name)	
			
			for sid in private_game_rooms_dictionary[private_room_name]:
				del sid_private_game_rooms_dictionary[sid]
				disconnect(sid)
				private_room_connected_players.remove(sid)
			
			close_room(private_room_name)
			del private_game_rooms_dictionary[private_room_name]
			app.logger.info("cleared room " + private_room_name)	
	except:
		app.logger.error("error disconnecting user from game room, perhaps user has already been disconnected")


# handler for the unique room code request from player in create room page
@socketIO.on('request_private_room_code')
def private_room_code():
	app.logger.info("Player " + str(request.sid) + " requested room code")
	room_code = get_unique_room_code()
	socketIO.emit('private_room_code', {'room_code': room_code}, room=request.sid)
	sid_private_game_rooms_dictionary[request.sid] = room_code
	private_game_rooms_dictionary[room_code] = [request.sid]
	private_room_connected_players.add(request.sid)
	join_room(room_code)


# notify the two players in the room of their colour (blue [1] or grey [0])
def notifyPrivateRoomPlayerColour():
	isPlayerBlue = None
	private_room_name = sid_private_game_rooms_dictionary[request.sid]
	for sid in private_game_rooms_dictionary[private_room_name]:
		try:
			isPlayerBlue = private_game_rooms_dictionary[private_room_name].index(sid)
			app.logger.info("player " + str(sid) + " colour is: " + str(isPlayerBlue))
		except:
			pass
		if isPlayerBlue == 0 or isPlayerBlue == 1:
			socketIO.emit('player_colour_assignment', {'isPlayerBlue': isPlayerBlue}, room=sid)


# handler for the join by room code request from player in join game page
@socketIO.on('join_by_private_room_code')
def private_room_code(json):
	try:
		app.logger.info("Player " + str(request.sid) + " requesting to join " + json['room_code'])
		if json['room_code'] in private_game_rooms_dictionary.keys():
			if len(private_game_rooms_dictionary[json['room_code']]) == 1:
				socketIO.emit('join_by_private_room_code_response', {'join_status': 1}, room=request.sid)
				sid_private_game_rooms_dictionary[request.sid] = json['room_code']
				private_game_rooms_dictionary[json['room_code']].append(request.sid)
				private_room_connected_players.add(request.sid)
				join_room(json['room_code'])
				socketIO.emit('start_game_private_room', room=json['room_code'])
				notifyPrivateRoomPlayerColour()
			elif (len(private_game_rooms_dictionary[json['room_code']])) < 1:
				socketIO.emit('join_by_private_room_code_response', {'join_status': 0}, room=request.sid)
			else:
				socketIO.emit('join_by_private_room_code_response', {'join_status': -1}, room=request.sid)
		else:
			socketIO.emit('join_by_private_room_code_response', {'join_status': 0}, room=request.sid)
	except:
		app.logger.error("error joining user by private game code")


# emits stone placements of the players to their room
@socketIO.on('stone_placement_private_room')
def stone_placement(json):
	socketIO.emit('placement_response_private_room', json, room=sid_private_game_rooms_dictionary[request.sid])

# ------------------------------------------------------------------------------------------
# shared SocketIO

# handler for user disconnection, triggered by SocketIO
@socketIO.on('disconnect')
def disconnect_handler():
	try:
		disconnect_from_game_room()
		disconnect_from_private_game_room()
	except:
		app.logger.error("error disconnecting user from game room, perhaps user has already been disconnected")


# ------------------------------------------------------------------------------------------
# http requests

# main welcome page
@app.route('/', methods=('GET', 'POST'))
def main_home():
	if request.method == 'POST':
		if 'play_button' in request.form:
			if request.form['play_button'] == 'start_game':
				return redirect(url_for('modes'))
		if 'license_info_button' in request.form:
			if request.form['license_info_button'] == 'show_license_info':
				return redirect(url_for('license_info'))

	return render_template('index.html')


# game modes select page
@app.route('/game_modes', methods=('GET', 'POST'))
def modes():
	if request.method == 'POST':
		if 'game_mode_button' in request.form:
			if request.form['game_mode_button'] == 'random_game':
				return redirect(url_for('random_game'))
			elif request.form['game_mode_button'] == 'create_room':
				return redirect(url_for('create_game_room'))
			elif request.form['game_mode_button'] == 'join_room':
				return redirect(url_for('join_game_room'))

	return render_template('modes.html')


# join game page
@app.route('/license_info', methods=['GET'])
def license_info():
	return render_template('license_page.html')


# random game page
@app.route('/random_game', methods=('GET', 'POST'))
def random_game():
	if request.method == 'POST':
		if 'corner_button' in request.form:
			if request.form['corner_button'] == 'exit_queue':
				return redirect(url_for('main_home'))

	return render_template('random_game.html')


# create game page
@app.route('/create_game', methods=['GET'])
def create_game_room():
	return render_template('create_room.html')


# join game page
@app.route('/join_game', methods=['GET'])
def join_game_room():
	return render_template('join_room.html')

# ------------------------------------------------------------------------------------------
# run app

if __name__ == '__main__':
	socketIO.run(app)
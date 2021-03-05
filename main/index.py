# The following license applies to Flask
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

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flask_socketio import emit, join_room, leave_room
from auth import login_required
from main import socketIO, app
from collections import deque

bp = Blueprint('index', __name__, url_prefix='/index')

@bp.route('/', methods=('GET', 'POST'))
def main_home():
    if request.method == 'POST':
        if 'corner_button' in request.form:
            if request.form['corner_button'] == 'sign_in':
                return redirect(url_for('auth.login'))

            elif request.form['corner_button'] == 'log_out':
                return redirect(url_for('auth.logout'))
                
        elif 'play_button' in request.form:
            if request.form['play_button'] == 'start_game':
                return redirect(url_for('index.game'))

    if (g.user is None):
        return render_template('index.html', is_signed_in = 0)
    else:
        user_info = (g.user.username + " / Wins: " + str(g.user.wins) + " / Losses: " + str(g.user.losses)
        + " / Level: " + str(g.user.level))
        return render_template('index.html', is_signed_in = 1, user_info = user_info)

@bp.route('/game', methods=['GET'])
@login_required
def game():
    game_message = 'Time Remaining: 00:00'
    return render_template('game.html', game_message=game_message)

@bp.route('/finding', methods=['GET'])
@login_required
def finding_game():
    return render_template('finding.html')

game_rooms_dictionary = dict()
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

# TODO add mutex for socketIO requests

@socketIO.on('request_room')
def request_game_room():
    if session.get('user_id') not in connectedPlayersList:
        connectedPlayersList.append(session.get('user_id'))

        app.logger.info(session.get('user_id'))

        for i in range(10):
            if 2 > len(game_rooms[i]):
                app.logger.info("# of players currently in room " + str(i) + " is (before adding): " + str(len(game_rooms[i])))
                game_rooms[i].append(session.get('user_id'))
                join_room(i)
                app.logger.info("Player " + str(session.get('user_id')) + " joined room number: " + str(i))
                game_rooms_dictionary[session.get('user_id')] = i
                app.logger.info("# of players currently in room " + str(i) + " is (after adding): " + str(len(game_rooms[i])))
                break

@socketIO.on('check_entered_room')
def check_entered_game_room():
    try:
        current_game_room_number = game_rooms_dictionary[session.get('user_id')]
        if len(game_rooms[current_game_room_number]) == 2:
            json = {'response': True}
        else:
            json = {'response': False}
        app.logger.info(current_game_room_number)
        app.logger.info(len(game_rooms[current_game_room_number]))
        # app.logger.info("size of game room number " + str(current_game_room_number) + ": " + len(game_rooms[current_game_room_number]))
        # app.logger.info("current game room number: " + str(current_game_room_number))
        socketIO.emit('check_entered_room_response', json, room=current_game_room_number)
    except:
        json = {'response': False}
        socketIO.emit('check_entered_room_response', json, room=current_game_room_number)
        
@socketIO.on('stone_placement')
def handle_my_custom_event(json):
    socketIO.emit('placement_response', json, room=game_rooms_dictionary[session.get('user_id')])


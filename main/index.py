# The following license applies to Flask
# Copyright 2010 Pallets
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Other code in file written by Augustine Jeong
# Copyright (c) 2021 Augustine Jeong

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from auth import login_required
from main import socketIO, app

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
def finding_game():
    return render_template('finding.html')

@socketIO.on('stone_placement')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    app.logger.info("received stone_placement")
    socketIO.emit('placement_response', json)
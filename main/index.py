from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from main.auth import login_required

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
    return render_template('game.html')

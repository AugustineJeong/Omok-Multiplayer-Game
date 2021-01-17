from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for


bp = Blueprint('index', __name__, url_prefix='/index')

@bp.route('/', methods=('GET', 'POST'))
def main_home():
    if request.method == 'POST':
        if request.form['corner_button'] == 'sign_in':
            return redirect(url_for('auth.login'))
        if request.form['corner_button'] == 'log_out':
            return redirect(url_for('auth.logout'))

    if (g.user is None):
        return render_template('index.html', is_signed_in = 0)
    else:
        return render_template('index.html', is_signed_in = 1)
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for


bp = Blueprint('index', __name__, url_prefix='/index')

@bp.route('/', methods=('GET', 'POST'))
def main_home():
    if request.method == 'POST':
        return redirect(url_for('auth.login'))

    return render_template('index.html')
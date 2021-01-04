import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from main.base import Base, Session
from main.user import User


bp = Blueprint('auth', __name__, url_prefix='/authentication')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        databaseSession = Session()

        username = request.form['username']
        password = request.form['password']

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else: 
            userExists = None
            try:
                userExists = (databaseSession.query(User).filter(User.username == username).first())
            except: 
                pass
            if (userExists is not None):
                error = 'Username {} already exists.'.format(username)
            
        if error is None:
            databaseSession.add(User(username, generate_password_hash(password)))
            databaseSession.commit()
            databaseSession.close()
            return redirect(url_for('auth.login'))
        else:
            databaseSession.commit()
            databaseSession.close()
            flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        databaseSession = Session()

        username = request.form['username']
        password = request.form['password']

        user = None
        try:
            user = databaseSession.query(User).filter(User.username==username).first()
        except:
            pass

        error = None

        if (user is None):
            error = 'Incorrect username or password.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect username or password.'

        databaseSession.close()

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
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


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
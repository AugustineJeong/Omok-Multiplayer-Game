# The following license applies to Flask
# Some of the code on this file have been based off of Flask's documentation.
# Copyright 2010 Pallets
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The following license applies to werkzeug
# Copyright 2007 Pallets
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2 .Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Other code in file written by Augustine Jeong
# Copyright (c) 2021 Augustine Jeong

import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from base import Session
from user import User


bp = Blueprint('auth', __name__, url_prefix='/authentication')

@bp.route('/register', methods=('GET', 'POST'))
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
            return redirect(url_for('auth.login'))
        else:
            databaseSession.commit()
            databaseSession.close()
            flash(error)

    if (g.user is not None):
        return redirect(url_for('index.main_home'))
    else:
        return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        if request.form['sign_in_screen_button'] == 'sign_up':
            return redirect(url_for('auth.register'))
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
                return redirect(url_for('index.main_home'))

            flash(error)

    if (g.user is not None):
        return redirect(url_for('index.main_home'))
    else:
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
    return redirect(url_for('index.main_home'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
# The following license applies to Flask
# Some of the code on this file have been based off of Flask's documentation.
# Copyright 2010 Pallets
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Other code in file written by Augustine Jeong
# Copyright (c) 2021 Augustine Jeong

import os

from flask import Flask
from sqlalchemy import create_engine

app_instance_path = ''

# creates and returns the actual flask application
def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app_instance_path = app.instance_path
	app.config.from_mapping(
		SECRET_KEY ='dev',
		DATABASE = 'sqlite:///' + os.path.join(app.instance_path, 'db.sqlite3')
	)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# add database to app
	from . import base
	base.init_app(app)
	
	# add auth blueprint to app
	from . import auth
	app.register_blueprint(auth.bp)

	# add index blueprint to app
	from . import index
	app.register_blueprint(index.bp)

	return app

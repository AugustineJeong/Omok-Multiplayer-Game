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

	if test_config is None:
		app.config.from_pyfile('config.py', silent=True)
	else:
		app.config.from_mapping(test_config)

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

	return app

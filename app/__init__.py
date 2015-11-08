# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flask.ext.assets import Environment, Bundle
from flask.ext.httpauth import HTTPBasicAuth


import os
import redis
from app.database import db, bcrypt



app = Flask(__name__)

app.config['S3_BUCKET_NAME'] = 'mapia'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/mapia.db'
app.config['ONLINE_LAST_MINUTES'] = 5 #5min
app.config['SESSION_ALIVE_MINUTES'] = 14400
app.config['SECRET_KEY'] = 'gi3mHUx8hcLoQrnqP1XOkSORrjxZVkST'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

app.config['PHOTO_UPLOAD_FOLDER'] = './app/static/photo/'
app.config['VIDEO_UPLOAD_FOLDER'] = './app/static/video/'
app.secret_key = app.config['SECRET_KEY']

r = redis.Redis(host='localhost', port=6379, db=0)


def create_app(config=None):
	print 'create app'

	r = redis.Redis(host='localhost', port=6379, db=0)
	app.redis = r	

	from app.mod_api.controllers import api
	# Initialize SQL Alchemy and Flask-Login
	# Instantiate the Bcrypt extension
	db = SQLAlchemy(app)
	db.init_app(app)
	bcrypt.init_app(app)
	# CSRF protection
	# csrf.init_app(app)

	# Web assets (js, less)
	assets = Environment(app)

	# js = Bundle('js/main.js',
	#             filters='jsmin', output='gen/bundle.js')
	# assets.register('js_all', js)

	# Automatically tear down SQLAlchemy
	@app.teardown_request
	def shutdown_session(exception=None):
	    db.session.remove()

	@app.before_request
	def before_request():
	    g.user = current_user


	app.register_blueprint(api)
	from app import views

	return app

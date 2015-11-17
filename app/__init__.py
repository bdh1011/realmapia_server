# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flask.ext.assets import Environment, Bundle
from flask.ext.httpauth import HTTPBasicAuth

import os
import redis
from app.database import db, bcrypt



#app.secret_key = app.config['SECRET_KEY']


app = Flask(__name__)
app.r = redis.Redis(host='localhost', port=6379, db=0)
app.config['S3_BUCKET_NAME'] = 'mapia'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mapia:1realmapia!@mapiadb.crtjr2nnqaxl.ap-northeast-1.rds.amazonaws.com'
app.config['ONLINE_LAST_MINUTES'] = 5
app.config['SESSION_ALIVE_MINUTES'] = 14400
app.config['SECRET_KEY'] = 'gi3mHUx8hcLoQrnqP1XOkSORrjxZVkST'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

app.config['PROFILE_PIC_UPLOAD_FOLDER']= './app/static/profile_pic/'
app.config['PHOTO_UPLOAD_FOLDER'] = './app/static/photo/'
app.config['VIDEO_UPLOAD_FOLDER'] = './app/static/video/'

app_name = 'mapia'
root_dir = os.path.dirname(os.getcwd())
app.config['PROFILE_PIC_DOWNLOAD_FOLDER']= os.path.join(root_dir, app_name,'app','static','profile_pic/')
app.config['PHOTO_DOWNLOAD_FOLDER'] = os.path.join(root_dir, app_name,'app','static','photo/')
app.config['VIDEO_DOWNLOAD_FOLDER'] = os.path.join(root_dir, app_name,'app','static','video/')

def create_app(config=None):

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

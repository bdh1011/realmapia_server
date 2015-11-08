from flask import Flask, redirect, url_for
from app import app

class Nil:
	def __init__(*args, **kwargs):
		pass
	def __call__(self):
		pass

@app.route('/')
@app.route('/login')
@app.route('/main')
def redirect_login():
	return Nil
	#return redirect(url_for('manage.login'))

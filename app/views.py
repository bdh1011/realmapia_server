from flask import Flask, redirect, url_for
from app import app


@app.route('/')
@app.route('/login')
@app.route('/main')
def redirect_login():
	return redirect(url_for('manage.login'))
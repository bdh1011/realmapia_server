from flask import Flask, redirect, url_for
from app import app
from . import celery

@app.celery.task(name='test')
def add_together(a, b):
    return a+b


@app.route('/add')
def testing():
    print celery
    task = add_together.apply_async(args=[23,42], countdown=10)
    # print task.wait()
    return task.state
    
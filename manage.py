# manage.py
from flask.ext.script import Shell, Manager, Server
from flask import current_app
from flask.ext.migrate import Migrate, MigrateCommand

from app.database import db
from app import models
from app import create_app
from flask_s3 import FlaskS3
import flask_s3
import logging, logging.config, yaml
import os

from flask.ext.cors import CORS

app = create_app()

manager = Manager(app)
migrate = Migrate()
cors = CORS(app)
migrate.init_app(app, db, directory="./migrations")
s3 = FlaskS3(app)


def _make_context():
    return dict(app=current_app, db=db, models=models)


server = Server(host="0.0.0.0", port=80)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command("shell", Shell(use_ipython=True, make_context=_make_context))
manager.add_command("runserver", server)
manager.add_command('db', MigrateCommand)



@manager.command
def createdb():
    db.init_app(current_app)
    db.create_all()

@manager.command
def dropdb():
    db.init_app(current_app)
    db.drop_all()

@manager.command
def testdb():
    from tests.test_database import APITestCase
    import unittest
    runner = unittest.TextTestRunner()
    runner.run(unittest.makeSuite(APITestCase))

@manager.command
def testall():
    testdb()


# @manager.command
# def run():
#     celery = make_celery()
#     manager.run()


if __name__ == "__main__":

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
	logging.config.dictConfig(yaml.load(open('logging.conf')))
	logfile    = logging.getLogger('file')
	logconsole = logging.getLogger('console')
	logfile.debug("Debug FILE")
	logconsole.debug("Debug CONSOLE")

	manager.run()
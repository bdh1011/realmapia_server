
S3_BUCKET_NAME = 'mapia'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/mapia.db'
ONLINE_LAST_MINUTES = 5
SESSION_ALIVE_MINUTES = 14400
SECRET_KEY = 'gi3mHUx8hcLoQrnqP1XOkSORrjxZVkST'
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

PROFILE_PIC_UPLOAD_FOLDER = './app/static/profile_pic/'
PHOTO_UPLOAD_FOLDER = './app/static/photo/'
VIDEO_UPLOAD_FOLDER = './app/static/video/'

PROFILE_PIC_DOWNLOAD_FOLDER = 'static/profile_pic/'
PHOTO_DOWNLOAD_FOLDER = 'static/photo/'
VIDEO_DOWNLOAD_FOLDER = 'static/video/'

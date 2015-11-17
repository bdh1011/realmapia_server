#!flask/bin/python
from app import create_app

if __name__ == '__main__':
	create_app().run(host="0.0.0.0", port=8080, debug=True, threaded=True)

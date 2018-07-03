from flask import Flask
from freshplaylist.factory import create_app
# app = Flask(__name__, static_folder='static')
# app.config.from_pyfile('config.py')
app = create_app()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
db = SQLAlchemy(app)

app.config.from_pyfile('config.py')

from app import views, models 

if __name__ == "__main__":
    app.run(port=8080)

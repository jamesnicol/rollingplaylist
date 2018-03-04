from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///test.db"
db = SQLAlchemy(app)

app.config.from_pyfile('config.py')

from app import views, models 

if __name__ == "__main__":
    app.run(port=8080)

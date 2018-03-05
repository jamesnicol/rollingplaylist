from flask import Flask
from flask_oauthlib.client import OAuth
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
app = Flask(__name__, instance_relative_config=True)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
# app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///test.db"
app.config.from_pyfile('config.py')
db_base = declarative_base()
db_engine = create_engine('sqlite:///test.db')
Session = sessionmaker(bind=db_engine)
# db = SQLAlchemy(app)

SPOTIFY_APP_ID = app.config["SPOTIFY_APP_ID"]
SPOTIFY_APP_SECRET = app.config["SPOTIFY_APP_SECRET"]

oauth = OAuth(app)
spotify = oauth.remote_app(
    'spotify',
    consumer_key=SPOTIFY_APP_ID,
    consumer_secret=SPOTIFY_APP_SECRET,
    request_token_params={
        'scope': 'user-read-email user-library-read playlist-modify-public'},
    base_url='https://api.spotify.com',
    request_token_url=None,
    access_token_url='https://accounts.spotify.com/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)

from app import views, models 

if __name__ == "__main__":
    app.run(port=8080)

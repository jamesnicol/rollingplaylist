from flask import Flask
from flask_oauthlib.client import OAuth
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

oauth = OAuth(app)
spotify = oauth.remote_app(
    'spotify',
    consumer_key=app.config["SPOTIFY_APP_ID"],
    consumer_secret=app.config["SPOTIFY_APP_SECRET"],
    request_token_params={
        'scope': 'user-read-email user-library-read playlist-modify-public'},
    base_url='https://api.spotify.com',
    request_token_url=None,
    access_token_url='https://accounts.spotify.com/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)

from app import views, models 

if __name__ == "__main__":
    app.run()

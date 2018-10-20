import os
from flask import Blueprint
from flask_oauthlib.client import OAuthException
from flask_oauthlib.client import OAuth


auth_bp = Blueprint('auth_bp', __name__, url_prefix='/login')


oauth = OAuth(auth_bp)
spotify = oauth.remote_app(
    'spotify',
    consumer_key=os.environ["SPOTIFY_APP_ID"],
    consumer_secret=os.environ["SPOTIFY_APP_SECRET"],
    request_token_params={
        'scope': 'user-read-email user-library-read playlist-modify-public'},
    base_url='https://api.spotify.com',
    request_token_url=None,
    access_token_url='https://accounts.spotify.com/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)

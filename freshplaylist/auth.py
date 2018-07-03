import requests
from flask import session, current_app
from flask_oauthlib.client import OAuth
from freshplaylist import app
from freshplaylist.models import db
from freshplaylist.models.user import User

oauth = OAuth(app)
with app.app_context():
    spotify = oauth.remote_app(
        'spotify',
        consumer_key=current_app.config["SPOTIFY_APP_ID"],
        consumer_secret=current_app.config["SPOTIFY_APP_SECRET"],
        request_token_params={
            'scope': 'user-read-email user-library-read playlist-modify-public'},
        base_url='https://api.spotify.com',
        request_token_url=None,
        access_token_url='https://accounts.spotify.com/api/token',
        authorize_url='https://accounts.spotify.com/authorize'
    )


@spotify.tokengetter
def get_spotify_user_token():
    user = get_current_user()
    if user is None:
        # use for user agnostic searches
        return (get_client_token(), '')
    tok = user.token
    if tok:
        tok.get_token()
        return (tok.access_token, '')
    return None


def get_current_user():
    try:
        user = db.session.query(User).filter_by(
            spotify_id=session['user_id']).first()
    except KeyError:
        print("no user in session")
        return None
    return user


def get_client_token():
    payload = {"grant_type": "client_credentials",
               "client_id": spotify.consumer_key,
               "client_secret": spotify.consumer_secret}
    resp = requests.post(spotify.access_token_url, data=payload)
    return resp['access_token']

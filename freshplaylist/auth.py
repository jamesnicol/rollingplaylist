import requests
import os
from flask import session, Blueprint, url_for, request, redirect
from flask_oauthlib.client import OAuthException
from flask_oauthlib.client import OAuth
from freshplaylist.models import db
from freshplaylist.models.user import User
from freshplaylist.models.token import Token


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


@auth_bp.route('/')
def login():
    callback = url_for(
        'auth_bp.spotify_authorized',
        _external=True
    )
    return spotify.authorize(callback=callback)


@auth_bp.route('/authorized')
def spotify_authorized():
    resp = spotify.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: {0}'.format(resp.message)

    me = spotify.get('/v1/me', token=(resp['access_token'], ''))

    user_id = me.data['id']
    session['user_id'] = user_id
    user = db.session.query(User).filter(User.spotify_id == user_id).first()
    if not user:
        user = User(user_id)
        tok = Token(user, **resp)
        user.token = tok
        db.session.add(user)
        db.session.commit()

    return redirect(url_for('main_bp.index'))


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

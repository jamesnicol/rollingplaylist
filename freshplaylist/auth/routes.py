import requests
import os
import json
import pickle
from datetime import datetime, timedelta
from flask import session, url_for, request, redirect, current_app
from flask_oauthlib.client import OAuthException
import freshplaylist
from freshplaylist.models import db
from freshplaylist.models.user import User
from freshplaylist.models.token import Token
from freshplaylist.auth import spotify, auth_bp

SPOTIFY_TOKEN_FILENAME = 'data/spotify.bin'
SPOTIFY_TOKEN_PATH = os.path.join(os.path.dirname(freshplaylist.__file__),
                                  SPOTIFY_TOKEN_FILENAME)


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


@spotify.tokengetter
def get_spotify_user_token():
    user = get_current_user()
    if user is None:
        # use for user agnostic searches
        return (get_client_token(), '')
    tok = user.token
    if tok:
        return (tok.get_token(), '')
    return None


def get_current_user():
    try:
        user = db.session.query(User).filter_by(
            spotify_id=session['user_id']).first()
    except KeyError:
        print("no user in session")
        return None
    except RuntimeError:
        # session probably doesn't exist
        return None
    return user


def get_client_token():
    try:
        with open(SPOTIFY_TOKEN_PATH, 'rb') as fd:
            token_d = pickle.load(fd)
    except IOError:
        token_d = {}
    if not token_d or token_d['expires'] < datetime.now():
        payload = {"grant_type": "client_credentials",
                   "client_id": spotify.consumer_key,
                   "client_secret": spotify.consumer_secret}
        resp = requests.post(spotify.access_token_url, data=payload)
        if resp.status_code != 200:
            return None
        data = resp.json()
        token_d['access_token'] = data['access_token']
        expires_in = data['expires_in']
        if expires_in is not None:
            token_d['expires'] = datetime.now() + timedelta(seconds=expires_in)
        with open(SPOTIFY_TOKEN_PATH, 'wb+') as fd:
            pickle.dump(token_d, fd)
    return token_d['access_token']

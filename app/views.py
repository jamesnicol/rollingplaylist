import os
import datetime
from flask import Flask, redirect, url_for, render_template, session, request
from flask_oauthlib.client import OAuthException
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from app import app, Session, spotify
from app.models import User, Playlist, Token


class PlaylistForm(FlaskForm):
    playlist_name = StringField('playlist_name', validators=[DataRequired()])
    stale_days = StringField('stale_days', validators=[DataRequired()])


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    callback = url_for(
        'spotify_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return spotify.authorize(callback=callback)


@app.route('/login/authorized')
def spotify_authorized():
    resp = spotify.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: {0}'.format(resp.message)

    # session['oauth_token'] = (resp['access_token'], '')
    me = spotify.get('/v1/me', token=(resp['access_token'], ''))

    user_id = me.data['id']
    db_session = Session()
    session['user_id'] = user_id
    user = db_session.query(User).filter(User.spotify_id == user_id).first()
    if not user:
        user = User(user_id)
        tok = Token(user, **resp)
        user.token = tok
        db_session.add(user)
        db_session.commit()

    info = '<html><body>Logged in as id={0} name={1} redirect={2}'.format(
        me.data['id'],
        me.data['display_name'],
        request.args.get('next'))
    info += '<br><a href=http://localhost:8080/cull_stale_tracks>cull stale</a>'
    info += '<br><a href=http://localhost:8080/create_rolling_playlist>create rolling playlist</a>'
    info += '<br><a href=http://localhost:8080/info/playlists>playlists</a></body></html>'
    return info


@app.route('/info/playlists')
def get_playlists():
    playlists_obj = spotify.get('/v1/me/playlists')
    playlists = [(playlist['name'], playlist['id'])
                 for playlist in playlists_obj.data['items']]
    html = "<html><body>"
    for (p_name, p_id) in playlists:
        html += '<br><a href=http://localhost:8080/info/playlist_tracks/{}>playlist: {}</a>'.format(
            p_id, p_name)
    html += "</body></html>"
    return html


@app.route('/make_rolling/<string:playlist>/<int:days_stale>/')
def rolling_playlist(playlist, days_stale):
    # todo check if real playlist
    db_session = Session()
    user = get_current_user(db_session)
    plst = Playlist(user, playlist, days_stale)
    user.playlists.append(plst)
    db_session.commit()

    return 'successfully made rolling playlist {}'.format(playlist)


@app.route('/cull_stale_tracks/')
def cull_stale_tracks():
    db_session = Session()
    playlists = db_session.query(Playlist).all()
    for p in playlists:
        p.cull_tracks()
    return "culled tracks"


@app.route('/create_rolling_playlist', methods=['POST', 'GET'])
def new_rolling_playlist():
    form = PlaylistForm()
    if form.validate_on_submit():
        db_session = Session()
        user = get_current_user(db_session)
        params = {'name': form.playlist_name.data}
        create_playlist_url = '/v1/users/{}/playlists'.format(user.spotify_id)
        resp = spotify.post(create_playlist_url, data=params, format='json')
        p_id = resp.data['id']
        plst = Playlist(user, p_id, form.stale_days.data)
        user.playlists.append(plst)
        db_session.commit()
        print("created playlist")
        return "created new playlist " + form.playlist_name.data
    else:
        return render_template('createPlaylist.html', form=form)


@spotify.tokengetter
def get_spotify_oauth_token():
    db_session = Session()
    user = get_current_user(db_session)
    if not user:
        return None
    tok = user.token
    if tok:
        tok.get_token()
        db_session.commit()
        return (tok.access_token, '')
    return None
    # return session.get('oauth_token')


def get_current_user(db_session):
    user = db_session.query(User).filter_by(
        spotify_id=session['user_id']).first()
    return user


if __name__ == '__main__':
    app.run(port=8080)

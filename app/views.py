import os
import datetime
from flask import Flask, redirect, url_for, render_template, session, request
from flask_oauthlib.client import OAuthException
from app import app, db, spotify
from app.models import User, Playlist, Token


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/login')
def login():
    callback = url_for(
        'spotify_authorized',
        _external=True
    )
    print(callback)
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

    info = '<html><body>Logged in as id={0} name={1} redirect={2}'.format(
        me.data['id'],
        me.data['display_name'],
        request.args.get('next'))
    info += '<br><a href={}>cull stale</a>'.format(
        url_for('cull_stale_tracks', _external=True))
    info += '<br><a href={}>create rolling playlist</a>'.format(
        url_for('new_rolling_playlist', _external=True))
    info += '<br><a href={}>playlists</a></body></html>'.format(
        url_for('get_playlists', _external=True))
    return redirect(url_for('index'))
    # render_template('base.html')


@app.route('/info/playlists')
def get_playlists():
    playlists_obj = spotify.get('/v1/me/playlists')
    playlists = [(playlist['name'], playlist['id'])
                 for playlist in playlists_obj.data['items']]
    html = "<html><body>"
    for (p_name, p_id) in playlists:
        html += '<br><p>id: {}, name: {}</a>'.format(p_id, p_name)
    html += "</body></html>"
    return html


@app.route('/make_rolling/<string:playlist>/<int:days_stale>/')
def rolling_playlist(playlist, days_stale):
    # todo check if real playlist
    user = get_current_user()
    plst = next((p for p in user.playlists if p.playlist_id == playlist), None)
    if plst:
        plst.stale_period_days = days_stale
    else:
        playlists_obj = spotify.get('/v1/users/{}/playlists/{}'.format(user.spotify_id,playlist))
        if playlists_obj.status != 200:
            return "playlist not owned by user"
        plst = Playlist(user, playlist, days_stale)
        user.playlists.append(plst)
    db.session.commit()

    return 'successfully made rolling playlist {}'.format(playlist)


@app.route('/cull_stale_tracks/')
def cull_stale_tracks():
    playlists = db.session.query(Playlist).all()
    for p in playlists:
        p.cull_tracks()
    return "culled tracks"


@app.route('/create_rolling_playlist', methods=['POST', 'GET'])
def new_rolling_playlist():
    try:
        if request.method == 'POST':
            user = get_current_user()
            if user is None:
                return render_template('bigmeessage.html', message="PLEASE LOGIN")
            params = {'name': request.form['playlist_name']}
            create_playlist_url = '/v1/users/{}/playlists'.format(user.spotify_id)
            resp = spotify.post(create_playlist_url, data=params, format='json')
            p_id = resp.data['id']
            plst = Playlist(user, p_id, request.form['days_stale'])
            user.playlists.append(plst)
            db.session.commit()
            print("created playlist")
            return render_template('bigmessage.html', message="CREATED NEW PLAYLIST")
    except:
        return render_template('bigmessage.html', message="OOPS! SOMETHING WENT WRONG")


@spotify.tokengetter
def get_spotify_oauth_token():
    user = get_current_user()
    if user is None:
        return None
    tok = user.token
    if tok:
        tok.get_token()
        db.session.commit()
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

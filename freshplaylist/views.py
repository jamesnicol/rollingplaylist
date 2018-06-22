import os
import datetime
from flask import Flask, redirect, url_for, render_template, session, request
from flask_oauthlib.client import OAuthException
from freshplaylist import app, db
from freshplaylist.auth import spotify, get_current_user
from freshplaylist.models.user import User
from freshplaylist.models.playlist import Playlist
from freshplaylist.models.token import Token
from freshplaylist.models.song import Song
from freshplaylist import hit_scrape


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/<path:path>')
def serve_static_file(path):
    return app.send_static_file(path)


@app.route('/login')
def login():
    callback = url_for(
        'spotify_authorized',
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

    return redirect(url_for('index'))


@app.route('/info/playlists')
def get_playlists():
    playlists_obj = spotify.get('/v1/me/playlists')
    playlists = ['id: {}, name: {}'.format(
        p['id'], p['name']) for p in playlists_obj.data['items']]
    return render_template('list.html', your_list=playlists)


@app.route('/make_rolling/<string:playlist>/<int:days_stale>/')
def rolling_playlist(playlist, days_stale):
    # todo check if real playlist
    user = get_current_user()
    plst = next((p for p in user.playlists if p.playlist_id == playlist), None)
    if plst:
        plst.stale_period_days = days_stale
    else:
        playlists_obj = spotify.get(
            '/v1/users/{}/playlists/{}'.format(user.spotify_id, playlist))
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


@app.route('/create_rolling_playlist', methods=['POST'])
def new_rolling_playlist():
    try:
        if request.method == 'POST':
            user = get_current_user()
            if user is None:
                return render_template('bigmessage.html',
                                       message="PLEASE LOGIN")
            params = {'name': request.form['playlist_name']}
            create_playlist_url = '/v1/users/{}/playlists'.format(
                user.spotify_id)
            resp = spotify.post(create_playlist_url,
                                data=params, format='json')
            p_id = resp.data['id']
            plst = Playlist(user, p_id, request.form['days_stale'])
            user.playlists.append(plst)
            db.session.commit()
    except Exception as e:
        print(e)
        return render_template('bigmessage.html',
                               message="OOPS! SOMETHING WENT WRONG")
    return render_template('bigmessage.html', message="CREATED NEW PLAYLIST")


@app.route('/hit_list')
def show_hit_list():
    hits = [', '.join(["= ".join([k, v]) for k, v in d.items()])
            for d in hit_scrape.get_hit_list()]
    return render_template('list.html', your_list=hits)

@app.route('/testsong')
def test_song_id():
    sng = db.session.query(Song).filter(Song.title == "No place").first()
    if not sng:
        sng = Song("No place", "Noplc", "Rufus")
        db.session.add(sng)
        db.session.commit()

    sng.get_id()

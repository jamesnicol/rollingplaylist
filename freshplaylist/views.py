import os
import datetime
from flask import render_template, request, Blueprint
from freshplaylist.models import db
from freshplaylist.auth import spotify, get_current_user
from freshplaylist.models.user import User
from freshplaylist.models.playlist import Playlist
from freshplaylist.models.token import Token
from freshplaylist.models.song import Song
from freshplaylist import hit_scrape

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
def index():
    return render_template('base.html')


@main_bp.route('/<path:path>')
def serve_static_file(path):
    return main_bp.send_static_file(path)


@main_bp.route('/info/playlists')
def get_playlists():
    playlists_obj = spotify.get('/v1/me/playlists')
    playlists = ['id: {}, name: {}'.format(
        p['id'], p['name']) for p in playlists_obj.data['items']]
    return render_template('list.html', your_list=playlists)


@main_bp.route('/make_rolling/<string:playlist>/<int:days_stale>/')
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


@main_bp.route('/cull_stale_tracks/')
def cull_stale_tracks():
    playlists = db.session.query(Playlist).all()
    for p in playlists:
        p.cull_tracks()
    return "culled tracks"


@main_bp.route('/create_rolling_playlist', methods=['POST'])
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


@main_bp.route('/hit_list')
def show_hit_list():
    hits = [', '.join(["= ".join([k, v]) for k, v in d.items()])
            for d in hit_scrape.get_hit_list()]
    return render_template('list.html', your_list=hits)

import os
import datetime
from flask import render_template, request, Blueprint, redirect
from freshplaylist.models import db
from freshplaylist.auth import spotify
from freshplaylist.auth.routes import get_current_user
from freshplaylist.models.user import User
from freshplaylist.models.playlist import FreshPlaylist, FollowPlaylist
from freshplaylist.models.token import Token
from freshplaylist.models.song import Song
from freshplaylist import hit_scrape


main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
def index():
    return render_template('base.html')


@main_bp.route('/info/playlists')
def get_playlists():
    playlists_obj = spotify.get('/v1/me/playlists')
    playlists = ['id: {}, name: {}'.format(
        p['id'], p['name']) for p in playlists_obj.data['items']]
    return render_template('list.html', your_list=playlists)


@main_bp.route('/make_rolling/<string:playlist>/<int:days_stale>/')
def rolling_playlist(playlist, days_stale):
    # todo check if real playlist
    # todo make post
    user = get_current_user()
    plst = next((p for p in user.playlists if p.playlist_id == playlist), None)
    if plst:
        plst.stale_period_days = days_stale
    else:
        playlists_obj = spotify.get(
            '/v1/users/{}/playlists/{}'.format(user.spotify_id, playlist))
        if playlists_obj.status != 200:
            return "playlist not owned by user"
        plst = FreshPlaylist(user, playlist, days_stale)
        user.playlists.append(plst)
    db.session.commit()

    return 'successfully made fresh playlist {}'.format(playlist)


@main_bp.route('/cull_stale_tracks', methods=['DELETE'])
def cull_stale_tracks():
    playlists = db.session.query(FreshPlaylist).all()
    for p in playlists:
        p.cull_tracks()
    return "culled tracks"


@main_bp.route('/create_rolling_playlist', methods=['POST'])
def new_rolling_playlist():
    message = ''
    try:
        user = get_current_user()
        if user is None:
            message = "PLEASE LOGIN"
        else:
            plst_name = request.form['playlist_name']
            days_stale = request.form['days_stale']
            plst = FreshPlaylist.new_spotify_playlist(user, plst_name,
                                                      days_stale)
            db.session.add(plst)
            db.session.commit()
            message = "CREATED NEW PLAYLIST"
    except Exception as e:
        print(e)
        message = "OOPS! SOMETHING WENT WRONG"
    return render_template('bigmessage.html', message=message)


@main_bp.route('/hit_list_subscribe', methods=['POST'])
def subscribe_hit_list():
    user = get_current_user()
    hit_scrape.subscribe(user)
    return render_template('bigmessage.html', message="PLAYLIST FOLLOWED")


@main_bp.route('/add_all_songs')
def add_songs():
    user = get_current_user()
    plst = db.session.query(FollowPlaylist).first()
    plst.add_songs(plst.songs)
    return render_template('bigmessage.html', message="ADDED SONGS")

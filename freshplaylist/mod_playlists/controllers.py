from flask import render_template, request
from freshplaylist import db
from freshplaylist.mod_auth import spotify
from freshplaylist.mod_auth.controllers import get_current_user
from mod_playlists import playlist_bp, triple_j
from mod_playlists.models.playlist import FreshPlaylist  # , FollowPlaylist
from mod_playlists.models.song import Song


@playlist_bp.route('/', methods=['GET'])
def get_playlists():
    playlists_obj = spotify.get('/v1/me/playlists')
    playlists = ['id: {}, name: {}'.format(
        p['id'], p['name']) for p in playlists_obj.data['items']]
    return render_template('list.html', your_list=playlists)


@playlist_bp.route('/make_rolling/', methods=['POST'])
def rolling_playlist():
    reqObj = request.get_json()
    # todo check if real playlist
    print(reqObj)
    return 'did nothing fix me {}'.format(reqObj)
    user = get_current_user()
    plst = next((p for p in user.playlists
                 if p.playlist_id == playlist), None)
    if plst:
        plst.stale_period_days = days_stale
    else:
        playlists_obj = spotify.get('/v1/users/{}/playlists/{}'
                                    .format(user.spotify_id, playlist))
        if playlists_obj.status != 200:
            return "playlist not owned by user"
        plst = FreshPlaylist(user, playlist, days_stale)
        user.playlists.append(plst)
    db.session.commit()

    message = 'MADE {} FRESH'.format(playlist)
    return render_template('bigmessage.html', message=message)


@playlist_bp.route('/cull_stale_tracks', methods=['DELETE'])
def cull_stale_tracks():
    playlists = db.session.query(FreshPlaylist).all()
    for p in playlists:
        p.cull_tracks()
    return "culled tracks"


@playlist_bp.route('/update_hitlists', methods=['PUT'])
def update_hitlists():
    triple_j.update_all()
    return "updated playlists"


@playlist_bp.route('/create_rolling_playlist', methods=['POST'])
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


@playlist_bp.route('/hit_list_subscribe', methods=['POST'])
def subscribe_hit_list():
    user = get_current_user()
    triple_j.subscribe(user)
    return render_template('bigmessage.html',
                           message="PLAYLIST FOLLOWED")


# @playlist_bp.route('/add_all_songs')
# def add_songs():
#     user = get_current_user()
#     plst = db.session.query(FollowPlaylist).first()
#     plst.add_songs(plst.songs)
#     return render_template('bigmessage.html', message="ADDED SONGS")

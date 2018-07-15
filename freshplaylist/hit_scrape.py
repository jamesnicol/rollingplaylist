import requests
import datetime
import json
from freshplaylist.auth import spotify
from freshplaylist.models.playlist import FollowPlaylist
from freshplaylist.models.song import Song
from freshplaylist.models import db

FOLLOW_TYPE = 'triple_j_hitlist'
HITLIST_URL = 'https://music.abcradio.net.au/api/v1/recordings/plays.json'


def subscribe(user, name="Triple j Hitlist"):
    plst = FollowPlaylist.new_spotify_playlist(user, FOLLOW_TYPE, name)
    db.session.add(plst)
    songs = add_hl_songs_to_db()
    plst.add_songs(songs)
    db.session.commit()


def update_all():
    songs = add_hl_songs_to_db()
    playlists = db.session.query(FollowPlaylist).\
        filter(FollowPlaylist.following == FOLLOW_TYPE)
    for p in playlists:
        p.update(songs)


def add_hl_songs_to_db():
    songs = get_hit_list_data()
    res = []
    for s in songs:
        title = s['title']
        artists = ", ".join([a['name'] for a in s['artists']])
        try:
            album = s['releases'][0]['title']
        except IndexError:
            album = 'Unreleased'

        sng = Song.get_song(title, artists, album)
        if sng is None:
            sng = add_song_to_db(title, artists, album)
            db.session.add(sng)
        res.append(sng)
    db.session.commit()
    return res


def add_song_to_db(title, artists, album):
            sng = Song(title, artists, album)
            # sng.get_id()
            # if sng.spotify_uri is None:
            #     # could not get spotify uri
            #     return None
            return sng


def get_hit_list_data():
    today = datetime.datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    last_week = today - datetime.timedelta(days=7)
    q_params = {'order': 'desc',
                'limit': 50,
                'service': 'triplej',
                'from': last_week.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'to': today.strftime('%Y-%m-%dT%H:%M:%SZ')}

    hit_html = requests.get(HITLIST_URL, params=q_params)

    data = json.loads(hit_html.text)
    return data['items']

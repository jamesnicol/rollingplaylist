import requests
import datetime
import json
from freshplaylist.auth import spotify
from freshplaylist.models.playlist import FollowPlaylist
from freshplaylist.models.song import Song

FOLLOW_TYPE = 'triple_j_hitlist'


def subscribe(user, name="Triple j Hitlist"):
    plst = FollowPlaylist.new_spotify_playlist(user, FOLLOW_TYPE, name)
    return


def update_all():
    songs = get_hit_list_songs()
    playlists = db.session.query(FollowPlaylist).\
        filter(FollowPlaylist.following == FOLLOW_TYPE)
    for p in playlists:
        p.update(songs)


def update_playlist(songs, plst):

    return


def get_hit_list_songs():
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
            sng = Song(s.title, s.artists, s.album)
            if sng.spotify_uri is not None:
                # could not get spotify uri
                continue
            db.session.add(sng)
        res.append(sng)
    db.session.commit()
    return res


def get_hit_list_data():
    today = datetime.datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    last_week = today - datetime.timedelta(days=7)
    q_params = {'order': 'desc',
                'limit': 50,
                'service': 'triplej',
                'from': last_week.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'to': today.strftime('%Y-%m-%dT%H:%M:%SZ')}

    hit_html = requests.get(
        'https://music.abcradio.net.au/api/v1/recordings/plays.json',
        params=q_params)

    data = json.loads(hit_html.text)
    return data['items']

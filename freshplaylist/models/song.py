import urllib.parse
import requests
import json
from freshplaylist.models import db
from freshplaylist.auth import spotify
from freshplaylist.auth.routes import get_current_user, get_client_token


class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, db.Sequence('song_id_seq'), primary_key=True)
    # the spotify id of the song
    spotify_uri = db.Column(db.String, unique=True)
    title = db.Column(db.String)
    album = db.Column(db.String)
    artists = db.Column(db.String)

    def __init__(self, title, artists, album):
        self.title = title
        self.album = album
        self.artists = artists
        # self.get_id()

    def get_id(self):
        if self.spotify_uri is not None:
            return self.spotify_uri
        query = 'title:{} artist:{}'.format(self.title, self.artists)
        query = query.replace(",", "")
        params = {'q': query,
                  'type': 'track',
                  'market': 'AU',
                  'limit': 1}
        headers = {'Authorization': 'Bearer ' + get_client_token(),
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'
                   }

        search_url = spotify.base_url + '/v1/search'
        print(search_url)
        resp = requests.get(search_url, params=params, headers=headers)
        data = json.loads(resp.text)
        # search_url = '/v1/search'
        # resp = spotify.get(search_url, data=params)
        # if resp.status != 200 or resp.data['tracks']['total'] < 1:
        #     # could not find the track
        #     print("Could not find track with query:\n{}".format(query))
        #     self.spotify_uri = None
        if resp.status_code != 200 or data['tracks']['total'] < 1:
            # could not find the track
            print("Could not find track with query:\n{}".format(query))
            self.spotify_uri = None
        else:
            self.spotify_uri = data['tracks']['items'][0]['uri']
        db.session.commit()
        return self.spotify_uri

    def get_id_async(self):
        if self.spotify_uri is not None:
            return self.spotify_uri
        query = 'title:{} artist:{}'.format(self.title, self.artists)
        query = query.replace(",", "")
        params = {'q': query,
                  'type': 'track',
                  'market': 'AU',
                  'limit': 1}
        headers = {'Authorization': get_client_token()}

        search_url = spotify.base_url + '/v1/search'
        print(search_url)
        resp = requests.get(search_url, data=params, headers=headers)
        if resp.status != 200 or resp.data['tracks']['total'] < 1:
            # could not find the track
            print("Could not find track with query:\n{}".format(query))
            self.spotify_uri = None
        else:
            self.spotify_uri = resp.data['tracks']['items'][0]['uri']
        db.session.commit()
        return self.spotify_uri

    @classmethod
    def get_song(cls, title, artists, album):
        sng = db.session.query(Song).\
            filter(Song.title == title).\
            filter(Song.artists == artists).\
            filter(Song.album == album).\
            first()
        return sng

    def __repr__(self):
        return "Song(title={}, artist={} , album={}, uri={})".format(
            self.title, self.artists, self.album, self.spotify_uri
        )

    def __eq__(self, other):
        if self.spotify_uri and other.spotify_uri:
            return self.spotify_uri == other.spotify_uri
        if self.title != other.title:
            return False
        if self.album != other.album:
            return False
        if self.artists != other.artists:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

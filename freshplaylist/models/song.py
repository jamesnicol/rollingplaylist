import urllib.parse
from freshplaylist.models import db
from freshplaylist.auth import spotify
from freshplaylist.auth.routes import get_current_user


class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, db.Sequence('song_id_seq'), primary_key=True)
    # the spotify id of the song
    spotify_uri = db.Column(db.String, unique=True)
    title = db.Column(db.String)
    album = db.Column(db.String)
    artists = db.Column(db.String)

    def __init__(self, title, album, artists):
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

        search_url = '/v1/search'
        resp = spotify.get(search_url, data=params)
        if resp.status != 200 or resp.data['tracks']['total'] < 1:
            # could not find the track
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
        return "Title: {}, artist(s): {} , album: {}, uri: {}\n".format(
            self.title, self.album, self.artists, self.spotify_uri
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

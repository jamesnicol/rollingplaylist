import urllib.parse
from freshplaylist.models import db
from freshplaylist.auth import spotify
from freshplaylist.auth.routes import get_current_user


class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, db.Sequence('song_id_seq'), primary_key=True)
    song_id = db.Column(db.String, unique=True)  # the spotify id of the song
    title = db.Column(db.String)
    album = db.Column(db.String)
    artists = db.Column(db.String)

    def __init__(self, title, album, artists):
        self.title = title
        self.album = album
        self.artists = artists
        self.get_id()

    def __repr__(self):
        return "Title: {}, artist(s): {} , album: {}\n".format(
            self.title, self.album, self.artists
        )

    def get_id(self):
        if self.song_id is not None:
            return self.song_id
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
            self.song_id = None
        else:
            self.song_id = resp.data['tracks']['items'][0]['id']
        db.session.commit()
        return self.song_id
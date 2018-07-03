from freshplaylist.models import db
from freshplaylist.auth import spotify, get_client_token


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

    def __repr__(self):
        return "Title: {}, artist(s): {} , album: {}\n".format(
            self.title, self.album, self.artists
        )

    def get_id(self):
        tracks = []
        query = 'track:"{}" artist:"{}"'.format(self.title, self.artists)
        query = query.replace(",", "")
        query = query.replace(" ", "%20")
        params = {'q': query,
                  'type': 'track',
                  'market': 'AU',
                  'limit': 1}
        search_url = '/v1/search'
        tracks = spotify.get(search_url,
                             format='json',
                             data=params)
        tracks = tracks + [track for track in playlists_obj.data['items']]

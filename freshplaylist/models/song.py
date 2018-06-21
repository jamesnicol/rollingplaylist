from freshplaylist import spotify, db

belongs_to = db.Table('belongs_to',
                      db.Column('song_id', db.Integer, db.ForeignKey(
                          Song.id), primary_key=True),
                      db.Column('playlist_id', db.Integer, db.ForeignKey(
                          Playlist.id), primary_key=True),
                      )


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

    def get_tracks(self):
        tracks = []
        tracks_url = '/v1/users/{}/playlists/{}/tracks'.format(
            self.p_user.spotify_id, self.playlist_id
        )
        while tracks_url:
            playlists_obj = spotify.get(tracks_url, token=(
                self.p_user.token.get_token(), ''))
            tracks = tracks + [track for track in playlists_obj.data['items']]
            tracks_url = playlists_obj.data['next']
        return tracks

    def remove_tracks(self, tracks):
        delete_tracks_url = '/v1/users/{}/playlists/{}/tracks'.format(
            self.p_user.spotify_id, self.playlist_id
        )
        track_del_data = {
            'tracks': []
        }
        for i in range(0, len(tracks), 100):
            track_del_data['tracks'] = [{'uri': t['uri']}
                                        for t in tracks[i:i+100]]
            spotify.delete(delete_tracks_url, data=track_del_data,
                           format='json', token=(self.p_user.token.get_token(), ''))
        return

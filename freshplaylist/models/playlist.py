from datetime import datetime, timedelta
from freshplaylist.models import db
from freshplaylist.auth import spotify
from freshplaylist.models.song import Song

belongs_to = db.Table('belongs_to',
                      db.Column('song_id', db.Integer, db.ForeignKey(
                                'songs.id'), primary_key=True),
                      db.Column('playlist_id', db.Integer, db.ForeignKey(
                                'playlists.id'), primary_key=True),
                      )


class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, db.Sequence(
                   'playlist_id_seq'), primary_key=True)
    playlist_id = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    p_type = db.Column(db.String(20))
    p_user = db.relationship("User", uselist=False, back_populates="playlists")

    __mapper_args__ = {
        'polymorphic_identity': 'playlist',
        'polymorphic_on': 'p_type',
    }

    def __init__(self, user, playlist_id):
        self.playlist_id = playlist_id
        self.p_user = user
        user.playlists.append(self)

    def get_tracks(self):
        tracks = []
        tracks_url = '/v1/users/{}/playlists/{}/tracks'.format(
            self.p_user.spotify_id, self.playlist_id
        )
        while tracks_url:
            playlists_obj = spotify.get(tracks_url)
            tracks = tracks + [track for track in playlists_obj.data['items']]
            tracks_url = playlists_obj.data['next']
        return tracks

    @classmethod
    def new_spotify_playlist(cls, user, name):
        create_playlist_url = '/v1/users/{}/playlists'.format(
            user.spotify_id)
        params = {'name': name}
        resp = spotify.post(create_playlist_url,
                            data=params, format='json')
        if resp.status != 200 and resp.status != 201:
            return None
        p_id = resp.data['id']
        plst = cls(user, p_id)
        return plst

    def __repr__(self):
        return "Playlist_id: {}\n".format(
            self.playlist_id
        )


class FreshPlaylist(Playlist):
    __tablename__ = 'fresh_playlists'
    id = db.Column(db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
    stale_period_days = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'fresh_playlist',
    }

    def __init__(self, user, playlist_id, days=0):
        self.stale_period_days = int(days)
        super(FreshPlaylist, self).__init__(user, playlist_id)

    @classmethod
    def new_spotify_playlist(cls, user, name, days=0):
        return super(FreshPlaylist, cls).new_spotify_playlist(user, name)

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
                           format='json',
                           token=(self.p_user.token.get_token(), ''))
        return

    def cull_tracks(self):
        if (self.stale_period_days > 0):
            stale_date = datetime.utcnow() - timedelta(
                days=self.stale_period_days)
            tracks = self.get_tracks()
            del_tracks = []
            for t in tracks:
                t_added = datetime.strptime(
                    t["added_at"], "%Y-%m-%dT%H:%M:%SZ")
                if t_added < stale_date:
                    del_tracks.append(t['track'])
            self.remove_tracks(del_tracks)

    def __repr__(self):
        return "Playlist_id: {}, stale after: {} Days\n".format(
            self.playlist_id, self.stale_period_days
        )


class FollowPlaylist(Playlist):
    __tablename__ = 'follow_playlists'
    id = db.Column(db.Integer, db.ForeignKey('playlists.id'),
                   primary_key=True)
    following = db.Column(db.String(50))
    songs = db.relationship("Song", secondary=belongs_to,
                            lazy='subquery',
                            backref=db.backref('pages', lazy=True))

    __mapper_args__ = {
        'polymorphic_identity': 'follow_playlist',
    }

    def __init__(self, user, playlist_id, following=None):
        self.following = following
        super(FollowPlaylist, self).__init__(user, playlist_id)

    def update(self, new_songs):
        """
        adds new songs to playlist skipping duplicates\n
        :param new_songs: a list of Song objects
        """
        songs_to_add = list(set(new_songs) - set(self.songs))
        self.add_songs(songs_to_add)

    def add_songs(self, new_songs):
        add_tracks_url = '/v1/users/{}/playlists/{}/tracks'.format(
            self.p_user.spotify_id, self.playlist_id
        )
        track_add_data = {}
        for i in range(0, len(new_songs), 100):
            track_add_data['uris'] = [t.spotify_uri
                                      for t in new_songs[i:i+100]]
            track_add_data['position'] = 0
            resp = spotify.post(add_tracks_url, data=track_add_data,
                                format='json')
            print(resp)
        self.songs += new_songs

    @classmethod
    def new_spotify_playlist(cls, user, following, name):
        plst = super(FollowPlaylist, cls).new_spotify_playlist(user, name)
        plst.following = following
        return plst

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
    stale_period_days = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    p_user = db.relationship("User", uselist=False, back_populates="playlists")
    songs = db.relationship("Song", secondary=belongs_to,
                            lazy='subquery',
                            backref=db.backref('pages', lazy=True))

    def __init__(self, user, playlist_id, days):
        self.playlist_id = playlist_id
        self.stale_period_days = int(days)
        self.p_user = user

    def __repr__(self):
        return "Playlist_id: {}, stale after: {} Days\n".format(
            self.playlist_id, self.stale_period_days
        )

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
        return

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
                           format='json',
                           token=(self.p_user.token.get_token(), ''))
        return

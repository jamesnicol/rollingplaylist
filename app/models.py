# from app import db
from sqlalchemy import ForeignKey, Sequence, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import requests
import json
from app import spotify, db_base, Session


class User(db_base):
    """todo: write docstring for this class"""
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    spotify_id = Column(String, unique=True)
    token = relationship("Token", uselist=False, back_populates="user")
    playlists = relationship("Playlist", back_populates="user")

    def __init__(self, spotify_id):
        self.spotify_id = spotify_id

    def __repr__(self):
        return "Spotify id: {}, spotify_token: {}\n".format(
            self.spotify_id, self.spotify_token
        )


class Playlist(db_base):
    __tablename__ = 'playlist'
    id = Column(Integer, Sequence('playlist_id_seq'), primary_key=True)
    playlist_id = Column(String, unique=True)
    stale_period_days = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", uselist=False, back_populates="playlists")

    def __init__(self, user, playlist_id, days):
        self.playlist_id = playlist_id
        self.stale_period_days = days
        self.user = user

    def __repr__(self):
        return "Playlist_id: {}, stale after: {} Days\n".format(
            self.playlist_id, self.stale_period_days
        )

    def cull_tracks(self):
        if (self.stale_period_days > 0):
            stale_date = datetime.utcnow() - timedelta(days=self.stale_period_days)
            tracks = self.get_tracks()
            del_tracks = []
            for t in tracks:
                t_added = datetime.strptime(
                    t["added_at"], "%Y-%m-%dT%H:%M:%SZ")
                if t_added < stale_date:
                    del_tracks.append(t['track'])
            self.remove_tracks( del_tracks)
        return

    def get_tracks(self):
        tracks = []
        tracks_url = '/v1/users/{}/playlists/{}/tracks'.format(
            self.user.spotify_id, self.playlist_id
        )
        while tracks_url:
            playlists_obj = spotify.get(tracks_url, token=(self.user.token.get_token(),''))
            tracks = tracks + [track for track in playlists_obj.data['items']]
            tracks_url = playlists_obj.data['next']
        return tracks

    def remove_tracks(self, tracks):
        delete_tracks_url = '/v1/users/{}/playlists/{}/tracks'.format(
            self.user.spotify_id, self.playlist_id
        )
        track_del_data = {
            'tracks': []
        }
        track_del_data['tracks'] = [{'uri': t['uri']} for t in tracks]
        # todo: add limit to 100
        spotify.delete(delete_tracks_url, data=track_del_data, format='json', token=(self.user.token.get_token(),''))
        return 

class Token(db_base):
    __tablename__ = 'token'
    id = Column(Integer, Sequence('token_id_seq'), primary_key=True)
    access_token = Column(String)
    refresh_token = Column(String)
    expires = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", uselist=False, back_populates="token")

    def __init__(self, user, **kwargs):
        self.user = user
        expires_in = kwargs.pop('expires_in', None)
        if expires_in is not None:
            self.expires = datetime.now() + timedelta(seconds=expires_in)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_token(self):
        if not self.expires or self.expires < datetime.now():
            payload = {"grant_type": "refresh_token",
                       "refresh_token": self.refresh_token,
                       "client_id": spotify.consumer_key,
                       "client_secret": spotify.consumer_secret}
            resp = requests.post(spotify.access_token_url, data=payload)
            data = resp.json()
            self.access_token = data['access_token']
            expires_in = data['expires_in']
            if expires_in is not None:
                self.expires = datetime.now() + timedelta(seconds=expires_in)
        return self.access_token

    def __repr__(self):
        return "access token: {}, refresh_token: {}, expiry time: {}\n".format(
            self.access_token, self.access_token, self.expires
        )

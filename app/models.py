# from app import db
from sqlalchemy import ForeignKey, Sequence, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import requests
import json
from app import db_base, Session


class User(db_base):
    """todo: write docstring for this class"""
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    spotify_id = Column(String, unique=True)
    # token_id = Column(Integer, ForeignKey('token.id'))
    # token = relationship("Token", uselist=False, back_populates="user")
    playlists = relationship("Playlist")

    def __init__(self, spotify_id, token):
        self.spotify_id = spotify_id
        # self.token = token

    def __repr__(self):
        return "Spotify id: {}, spotify_token: {}\n".format(
            self.spotify_id, self.spotify_token
        )


class Playlist(db_base):
    __tablename__ = 'playlist'
    id = Column(Integer, Sequence('playlist_id_seq'), primary_key=True)
    playlist_id = Column(String, primary_key=True, unique=True)
    stale_period_days = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, playlist_id, days):
        self.playlist_id = playlist_id
        self.stale_period_days = days

    def __repr__(self):
        return "Playlist_id: {}, stale after: {} Days\n".format(
            self.playlist_id, self.stale_period_days
        )


class Token(db_base):
    __tablename__ = 'token'
    id = Column(Integer, Sequence('token_id_seq'), primary_key=True)
    access_token = Column(String)
    refresh_token = Column(String)
    expires = Column(DateTime)

    # user = relationship("User", uselist=False, back_populates="token")

    def __init__(self, **kwargs):
        expires_in = kwargs.pop('expires_in', None)
        if expires_in is not None:
            self.expires = datetime.now() + timedelta(seconds=expires_in)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_token(self, spotify):
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

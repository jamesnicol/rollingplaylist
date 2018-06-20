from datetime import datetime, timedelta
import requests
from freshplaylist import spotify, db

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, db.Sequence('token_id_seq'), primary_key=True)
    access_token = db.Column(db.String)
    refresh_token = db.Column(db.String)
    expires = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    t_user = db.relationship("User", uselist=False, back_populates="token")

    def __init__(self, user, **kwargs):
        self.t_user = user
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

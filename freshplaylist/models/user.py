from freshplaylist import db

class User(db.Model):
    """todo: write docstring for this class"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    spotify_id = db.Column(db.String, unique=True)
    token = db.relationship("Tokens", uselist=False, back_populates="user")
    playlists = db.relationship("Playlists", back_populates="user")

    def __init__(self, spotify_id):
        self.spotify_id = spotify_id

    def __repr__(self):
        return "Spotify id: {}, spotify_token: {}\n".format(
            self.spotify_id, self.token
        )

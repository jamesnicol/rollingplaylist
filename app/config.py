import os
DEBUG=False
SECRET_KEY=os.urandom(24)
SPOTIFY_APP_ID=os.environ.get('SPOTIFY_APP_ID')
SPOTIFY_APP_SECRET=os.environ.get('SPOTIFY_APP_SECRET')
SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS=False
SERVER_NAME=os.environ.get('SERVER_NAME')
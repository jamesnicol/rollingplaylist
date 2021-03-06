import os
DEBUG=False
SECRET_KEY=os.environ.get('APP_SECRET_KEY')
SPOTIFY_APP_ID=os.environ.get('SPOTIFY_APP_ID')
SPOTIFY_APP_SECRET=os.environ.get('SPOTIFY_APP_SECRET')
SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS=False
SERVER_NAME=os.environ.get('SERVER_NAME')
CLIENT_ACCESS_TOKEN=None
CLIENT_TOKEN_EXPIRES=None

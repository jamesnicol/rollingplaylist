# Freshplaylists
A tool to keep spotify playlists fresh
## Setup
1. Set the environment variables
2. Use Python 3.6
3. Form the project root, run:   
```python createdb.py```

## To run
```flask run [-p PORT_NUM -h HOST_NAME]```   
note: port num and host name must match ```SERVER_NAME```


## Environment variables

Make sure that these environment variables are set   
```
APP_SECRET_KEY=*some random key*
SPOTIFY_APP_ID=*your spotify app id*
SPOTIFY_APP_SECRET=*your spotify app key*
SERVER_NAME=*an address e.g. localhost.localdom:8080*
DATABASE_URL='sqlite:///DATABSE_NAME'
FLASK_ENV='development'
FLASK_APP='freshplaylist'
```
note: ```SERVER_NAME``` must have a ```'.'``` in it for modern browsers to consider it a valid domain for sessions to work (e.g. add localhost.localdom to your hosts file)
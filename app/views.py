from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth, OAuthException
from app import app
import os

SPOTIFY_APP_ID = os.environ["SPOTIFY_APP_ID"]
SPOTIFY_APP_SECRET = os.environ["SPOTIFY_APP_SECRET"]
oauth = OAuth(app)
spotify = oauth.remote_app(
    'spotify',
    consumer_key=SPOTIFY_APP_ID,
    consumer_secret=SPOTIFY_APP_SECRET,
    request_token_params={
        'scope': 'user-read-email user-library-read playlist-modify-public'},
    base_url='https://api.spotify.com',
    request_token_url=None,
    access_token_url='https://accounts.spotify.com/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    callback = url_for(
        'spotify_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return spotify.authorize(callback=callback)


@app.route('/login/authorized')
def spotify_authorized():
    resp = spotify.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: {0}'.format(resp.message)

    session['oauth_token'] = (resp['access_token'], '')
    me = spotify.get('/v1/me')

    user_id = me.data['id']

    info = '<html><body>Logged in as id={0} name={1} redirect={2}'.format(
        me.data['id'],
        me.data['display_name'],
        request.args.get('next')) + '<br><a href=http://localhost:8080/rolling>rolling</a>'
    info += '<br><a href=http://localhost:8080/info/tracks>tracks</a></body></html>'
    return info


@app.route('/info/tracks')
def get_tracks():
    track_obj = spotify.get('/v1/me/tracks')
    tracks = [(track['track']['name'], track['track']['artists'][0]['name'])
              for track in track_obj.data['items']]
    html = "<html><body>"
    for (t_name, t_artist) in tracks:
        html += '<br>track: {} by {}\n'.format(t_name, t_artist)
    html += "</body></html>"
    return html


@app.route('/rolling')
def rolling_playlist():
    create_playlist("Rolling")
    return ''


def create_playlist(name):
    params = {'name': name}
    user_id = spotify.get('/v1/me').data['id']
    resp = spotify.post('/v1/users/' + str(user_id) +
                        '/playlists', data=params, format='json')
    print("created playlist")
    return "created new playlist" + name


@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run(port=8080)

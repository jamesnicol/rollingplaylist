import os
import datetime
from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth, OAuthException
from app import app

SPOTIFY_APP_ID = app.config["SPOTIFY_APP_ID"]
SPOTIFY_APP_SECRET = app.config["SPOTIFY_APP_SECRET"]

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
    info += '<br><a href=http://localhost:8080/info/tracks>tracks</a>'
    info += '<br><a href=http://localhost:8080/info/playlists>playlists</a></body></html>'
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


@app.route('/info/playlists')
def get_playlists():
    playlists_obj = spotify.get('/v1/me/playlists')
    playlists = [(playlist['name'], playlist['id'])
                 for playlist in playlists_obj.data['items']]
    html = "<html><body>"
    for (p_name, p_id) in playlists:
        html += '<br><a href=http://localhost:8080/info/playlist_tracks/{}>playlist: {}</a>'.format(
            p_id, p_name)
    html += "</body></html>"
    return html


@app.route('/info/playlist_tracks/<p_id>/')
def show_playlist_tracks(p_id):
    tracks = get_playlist_tracks(p_id)
    html = "<html><body>"
    for t in tracks:
        html += '<br><a href=http://localhost:8080/delete_track/{0}/{1}>track: {1} by {2}\n</a>'.format(
            p_id, t['track']['name'], t['added_at'])
    html += "</body></html>"
    return html


def get_playlist_tracks(p_id):
    tracks = []
    user_id = spotify.get('v1/me').data['id']
    get_str = '/v1/users/' + user_id + '/playlists/' + p_id + '/tracks'
    while get_str:
        playlists_obj = spotify.get(get_str)
        tracks = tracks + [track for track in playlists_obj.data['items']]
        get_str = playlists_obj.data['next']
    return tracks


@app.route('/delete_track/<playlist>/<track>/')
def remove_track(playlist, track):
    user_id = spotify.get('v1/me').data['id']
    delete_endpoint = '/v1/users/' + user_id + '/playlists/' + playlist + '/tracks'
    track_del_data = {
        'tracks': [{'uri': track}]
    }
    resp = spotify.delete(delete_endpoint, data=track_del_data, format='json')
    return redirect(url_for('show_playlist_tracks', p_id=playlist))


@app.route('/delete_tracks/<playlist>/<track>/')
def remove_tracks(playlist, tracks):
    user_id = spotify.get('v1/me').data['id']
    delete_endpoint = '/v1/users/' + user_id + '/playlists/' + playlist + '/tracks'
    track_del_data = {
        'tracks': []
    }
    track_del_data['tracks'] = [{'uri': t['uri']} for t in tracks]
    # todo: add limit to 100
    resp = spotify.delete(delete_endpoint, data=track_del_data, format='json')
    return redirect(url_for('show_playlist_tracks', p_id=playlist))


@app.route('/remove_stale_tracks/<string:playlist>/<int:days>/', methods=['delete'])
def remove_tracks_after_date(playlist,days):  
    stale_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    tracks = get_playlist_tracks(playlist)
    del_tracks = []
    for t in tracks:
        t_added = datetime.datetime.strptime(
            t["added_at"], "%Y-%m-%dT%H:%M:%SZ")
        if t_added < stale_date:
            del_tracks.append(t['track'])
            # remove_track(playlist, t['track']['id'])
    remove_tracks(playlist, del_tracks)
    return redirect(url_for('show_playlist_tracks', p_id=playlist))


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

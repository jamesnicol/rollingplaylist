import freshplaylist.hit_scrape as hit_scrape
from freshplaylist.models.song import Song
from freshplaylist.models.user import User
from freshplaylist.models.playlist import FollowPlaylist


def test_get_data():
    data = hit_scrape.get_hit_list_data()
    assert isinstance(data, list)
    assert len(data) > 0
    song = data[0]
    assert 'title' in song
    assert 'artists' in song


def test_get_songs(db):
    songs = hit_scrape.add_hl_songs_to_db()
    assert isinstance(songs, list)
    assert len(songs) > 0
    song = songs[0]
    assert song.id is not None
    assert song.id > 0
    song.get_id()
    print(song)
    assert song.spotify_uri is not None
    assert isinstance(song, Song)


def test_get_songs_async(db):
    songs = hit_scrape.add_hl_songs_to_db()
    Song.get_ids(songs)
    song = songs[0]
    artist = song.artists
    title = song.title
    sngq = db.session.query(Song).filter(
        Song.artists == artist, Song.title == title).first()
    assert sngq.spotify_uri is not None


def test_get_songs_sync(db):
    songs = hit_scrape.add_hl_songs_to_db()[:3]
    for s in songs:
        s.get_id()
    song = songs[0]
    artist = song.artists
    title = song.title
    sngq = db.session.query(Song).filter(
        Song.artists == artist, Song.title == title).first()
    assert sngq.spotify_uri is not None


def test_subscribe(app, db):
    pseudo_spotify_id = "notaspotifyuser"
    user = User(pseudo_spotify_id)
    playlist_name = "The hit list"
    hit_scrape.subscribe(user, playlist_name)
    plst = (db.session.query(Song, FollowPlaylist)
            .filter(User.spotify_id == pseudo_spotify_id)
            .filter(FollowPlaylist.user_id == User.id)
            .filter(FollowPlaylist.p_type == hit_scrape.FOLLOW_TYPE)
            .first())
    assert plst is not None

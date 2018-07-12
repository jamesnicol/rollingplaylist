from freshplaylist.hit_scrape import *
from freshplaylist.models.song import Song


def test_get_data():
    data = get_hit_list_data()
    assert isinstance(data, list)
    assert len(data) > 0
    song = data[0]
    assert 'title' in song
    assert 'artists' in song


def test_get_songs(db):
    songs = add_hl_songs_to_db()
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
    songs = add_hl_songs_to_db()[:5]
    Song.get_ids(songs)
    song = songs[0]
    artist = song.artists
    title = song.title
    sngq = db.session.query(Song).filter(
        Song.artists == artist, Song.title == title).first()
    assert sngq.spotify_uri is not None


def test_get_songs_sync(db):
    songs = add_hl_songs_to_db()[:3]
    for s in songs:
        s.get_id()
    assert True

# def test_subscribe(app, db)

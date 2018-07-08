from freshplaylist.models.song import Song


def test_create_song(db):
    sng = Song("No place", "Noplc", "Rufus")
    db.session.add(sng)
    db.session.commit()

    assert sng.id >= 1

def test_get_song_id(db):
    sng = db.session.query(Song).filter(Song.title == "No place").first()
    sng.get_id()
    assert sng.song_id is not None

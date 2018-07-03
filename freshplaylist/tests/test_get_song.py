from freshplaylist.models.song import Song
from freshplaylist import app
from freshplaylist.models import db
from tests.conftest import session
import tempfile


def test_get_song(session):
    sng = Song("No place", "Noplc", "Rufus")
    db.session.add(sng)
    db.session.commit()

    print(sng.get_id())
    assert True


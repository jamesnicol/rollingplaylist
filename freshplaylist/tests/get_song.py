from freshplaylist.models.song import Song
from freshplaylist import db

sng = db.session.query(Song).filer(Song.title == "No place")
if not sng:
    sng = Song("No place", "Noplc", "Rufus")
    db.session.add(sng)
    db.session.commit()

sng.get_id()

from freshplaylist.views import cull_stale_tracks, update_hitlists
from freshplaylist.factory import create_app

app = create_app()
with app.app_context():
    update_hitlists()
    cull_stale_tracks()

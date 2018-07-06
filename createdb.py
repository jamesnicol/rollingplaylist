#!flask/bin/python
from freshplaylist.models import db
from freshplaylist.factory import create_app
app = create_app()
with app.app_context():
    db.create_all()

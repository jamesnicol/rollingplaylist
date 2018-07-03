#!flask/bin/python
from freshplaylist import app
from freshplaylist.models import db
with app.app_context():
    db.create_all()

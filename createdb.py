#!flask/bin/python
from migrate.versioning import api

from app import db
db.create_all()
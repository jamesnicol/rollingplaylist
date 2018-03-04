#!flask/bin/python
# from app import db
# db.create_all()

from app import models
models.create_tables()
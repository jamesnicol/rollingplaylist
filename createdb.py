#!flask/bin/python
# from app import db
# db.create_all()

from app import db_engine, db_base

db_base.metadata.create_all(db_engine)

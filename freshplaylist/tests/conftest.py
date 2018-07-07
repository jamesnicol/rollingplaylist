import os
import tempfile
import pytest
import freshplaylist
from freshplaylist.models import db as _db
from freshplaylist.factory import create_app

# from http://alexmic.net/flask-sqlalchemy-pytest/

TESTDB = 'data/test.db'
TESTDB_PATH = os.path.join(os.path.dirname(freshplaylist.__file__), TESTDB)
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH


@pytest.fixture(scope='session')
def app():
    """session-wide test application"""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI
    }
    app = create_app(settings_override)

    # establish an application context before running tests
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """session-wide test db"""
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    _db.create_all()

    yield _db

    _db.drop_all()
    os.unlink(TESTDB_PATH)

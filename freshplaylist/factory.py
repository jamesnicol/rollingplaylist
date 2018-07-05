from flask import Flask
from freshplaylist.models import db


def create_app(test_config=None):
    """create and configure the app"""
    app = Flask(__name__, static_folder='static')
    app.config.from_pyfile('config.py')

    if test_config is not None:
        app.config.from_mapping(test_config)

    db.init_app(app)

    from freshplaylist.views import main_bp
    app.register_blueprint(main_bp)

    from freshplaylist.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app

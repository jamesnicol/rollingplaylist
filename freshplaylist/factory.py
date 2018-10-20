from flask import Flask, url_for, render_template
from freshplaylist import db


def page_not_found(error):
    return render_template('404.html'), 404


def create_app(test_config=None):
    """create and configure the app"""
    app = Flask(__name__, static_folder='static')
    app.config.from_pyfile('config.py')
    app.register_error_handler(404, page_not_found)
    if test_config is not None:
        app.config.from_mapping(test_config)

    db.init_app(app)

    from freshplaylist.views import main_bp
    app.register_blueprint(main_bp)

    from freshplaylist.mod_auth import auth_bp
    app.register_blueprint(auth_bp)

    from freshplaylist.mod_playlists import playlist_bp
    app.register_blueprint(playlist_bp)

    return app

#!env/bin/python3
from freshplaylist.factory import create_app

if __name__ == "__main__":
    app = create_app()
    app.run()

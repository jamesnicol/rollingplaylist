#!env/bin/python3
from freshplaylist.factory import create_app
app = create_app()

if __name__ == "__main__":
    app.run()

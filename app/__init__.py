from flask import Flask
#from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "spotify_app_key_change_me"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testdb.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)


from app import views#spotipy 

if __name__ == "__main__":
  app.run(port=8080)

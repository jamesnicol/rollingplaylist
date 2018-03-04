from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
app = Flask(__name__, instance_relative_config=True)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
# app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///test.db"
app.config.from_pyfile('config.py')
db_base = declarative_base()
db_engine = create_engine('sqlite:///test.db')
Session = sessionmaker(bind=db_engine)
# db = SQLAlchemy(app)


from app import views, models 

if __name__ == "__main__":
    app.run(port=8080)

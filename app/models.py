from app import db
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class User(Base):
  """todo: write docstring for this class"""
  __tablename__ = 'user_table'
  id = Column(Integer, primary_key=True)
  spotify_id = Column(String)
  spotify_token = Column(String)
  stale_period_days = Column(Integer)

  def __init__(self, spotify_id, token):
    self.spotify_id = spotify_id
    self.spotify_token = token
  
  def set_stale_period(self, days):
    self.stale_period_days = days

def create_tables():
  engine = create_engine('sqlite:///test.db')
  Base.metadata.create_all(engine)

#todo: put these functions into a class?
# def addNewUser(email,name,password):
#   new_ex = User(email,name,password)
#   db.session.add(new_ex)
#   db.session.commit()

# def userExists(email):
#   test = User.query.filter(User.email == email).first()
#   if test is not None:
#     return True
#   else:
#     return False

# def findPassword(email):
#   test = User.query.filter(User.email == email).first()      
#   return (test.password)
# def findName(email):
#   test = User.query.filter(User.email == email).first()      
#   return (test.name)




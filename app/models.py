from app import db

class User(db.Model):
  """todo: write docstring for this class"""
  id = db.Column(db.Integer, primary_key=True)
  spotify_id = db.Column(db.String)
  spotify_token = db.Column(db.String)
  stale_period_days = db.Column(db.Integer)

  def __init__(self, spotify_id, token):
    self.spotify_id = spotify_id
    self.spotify_token = token
  
  def set_stale_period(self, days):
    self.stale_period_days = days

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




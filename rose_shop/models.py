from werkzeug.security import generate_password_hash #allows us to generate a hashed password
from flask_sqlalchemy import SQLAlchemy #allows our database to read our classes/objects as tables/rows 
from flask_login import UserMixin, LoginManager #allows us to load a current logged in user
from datetime import datetime
import uuid #generate a unique id (basically the same serializing last week)



db = SQLAlchemy() #instantiate our database
login_manager = LoginManager() #instantiate our login manager



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) #this queries our database & brings back the user with the same id



class User(db.Model, UserMixin):
    #think of this part as the CREATE TABLE 'User' 
    user_id = db.Column(db.String, primary_key = True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    #think of our __init__() as our INSERT INTO 
    def __init__(self, username, email, password, first_name="", last_name=""):
        self.user_id = self.set_id() #method to create a unique id
        self.first_name = first_name
        self.last_name = last_name 
        self.username = username
        self.email = email
        self.password = self.set_password(password) #method to hash our password for security 


    def set_id(self):
        return str(uuid.uuid4())
    

    def set_password(self, password):
        return generate_password_hash(password)
    

    def __repr__(self):
        return f"<USER: {self.username}"
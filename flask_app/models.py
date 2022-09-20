from datetime import datetime, timedelta
import jwt
from . import db, bcrypt, app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def generate_token(self):
        return jwt.encode({"id": self.id, "username":self.username, "exp":datetime.now() + timedelta(hours=1)}, app.config['SECRET_KEY'])



class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    views = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.String, nullable=True)

    def __repr__(self):
        return self.title

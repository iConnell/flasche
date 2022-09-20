from datetime import datetime, timedelta
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)



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


@app.route('/api/register', methods=['POST'])
def register_view():

    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if username is None or email is None or password is None:
        abort(400, "Missing a required field")
    
    if User.query.filter_by(username=username).first() is not None and User.query.filter_by(email=email).first() is not None:
        abort(400, "username or email already exists")

    user = User()
    for key, value in request.json.items():
        user.__setattr__(key, value)

    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    

    token = user.generate_token()

    response = {"token": token, "user":{
        "id": user.id,
        "username":user.username,
    }}
    return jsonify(response), 201

if __name__ == '__main__':
    app.run(debug=True)
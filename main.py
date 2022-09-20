from datetime import datetime, timedelta
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt
from functools import wraps


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return {"error": "Unauthorized"}, 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = User.query.filter_by(id=data['id'])
            if user is None:
                return {"error": "Unauthorized"}, 401
        except Exception:
            return {"error": "Something went wrong"}, 500

        #Adds the authenticated user to the request object
        request.user = user
        return f(*args, **kwargs)

    return decorated



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


@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Todo
    # Implement username or email authentication
    # email = request.json.get('email')

    if username is None or password is None:
        return {"error": "Enter username and password"}, 400
    
    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"error": "Username or password incorrect"}), 401
    
    if not user.check_password(password):
        return jsonify({"error": "Username orjjj password incorrect"}), 401

    token = user.generate_token()
    response = {"token": token, "user":{
        "id": user.id,
        "username":user.username,
    }}

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)
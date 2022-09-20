from flask_app import app, db
from flask import request, abort, jsonify
from .models import User

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
        return jsonify({"error": "Username or password incorrect"}), 401

    token = user.generate_token()
    response = {"token": token, "user":{
        "id": user.id,
        "username":user.username,
    }}

    return jsonify(response), 200

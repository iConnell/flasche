from functools import wraps
from flask import request
import jwt
from .models import User
from . import app

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

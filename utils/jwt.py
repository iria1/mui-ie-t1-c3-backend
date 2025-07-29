from flask import request, jsonify
import jwt
from datetime import datetime, timezone
from functools import wraps
from .config import JWT_SECRET, JWT_EXPIRY

def create_jwt():
    payload = {
        "exp": datetime.now(timezone.utc) + JWT_EXPIRY,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_jwt(token):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth_header.split(" ")[1]
        try:
            decode_jwt(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated
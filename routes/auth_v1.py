from flask import Blueprint, request, jsonify
from utils.config import SECRET_PASSWORD
from utils.jwt import create_jwt, require_token

auth_v1_bp = Blueprint('auth_v1_bp', __name__, url_prefix='/v1/auth')

@auth_v1_bp.route('/login', methods=["POST"])
def login():
    data = request.get_json()
    if not data or data.get("password") != SECRET_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401
    token = create_jwt()
    return jsonify({"token": token})

@auth_v1_bp.route('/verify')
@require_token
def verify():
    return jsonify({"message": "OK"}), 200
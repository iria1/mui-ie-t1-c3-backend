from flask import Blueprint, jsonify
from .charts_v1 import charts_v1_bp
from .charts_v2 import charts_v2_bp
from .chatbot_v1 import chatbot_v1_bp
from .auth_v1 import auth_v1_bp

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

api_bp.register_blueprint(charts_v1_bp)
api_bp.register_blueprint(charts_v2_bp)
api_bp.register_blueprint(chatbot_v1_bp)
api_bp.register_blueprint(auth_v1_bp)

@api_bp.route('/')
def index():
    # health check
    return jsonify({
        "status": "OK"
    }), 200
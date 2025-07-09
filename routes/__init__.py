from flask import Blueprint, jsonify
from .charts import charts_bp
from .chatbot import chatbot_bp

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

api_bp.register_blueprint(charts_bp)
api_bp.register_blueprint(chatbot_bp)

@api_bp.route('/')
def index():
    # health check
    return jsonify({
        "status": "OK"
    }), 200
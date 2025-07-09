from flask import Blueprint, request, jsonify, abort
from models import WordCloud, BullyStatRegional, SocmedMental
from sqlalchemy import func
from werkzeug.exceptions import BadRequest
from utils import validate_request_params, sanitize_string

chatbot_bp = Blueprint('chatbot_bp', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/get_response_from_chatbot', methods=['POST'])
def get_response_from_chatbot():
    if not request.is_json:
        abort(400, description='Request must be JSON')
    
    is_valid, error_response = validate_request_params(request, ['message'])
    if not is_valid:
        abort(400, description=error_response)

    data = request.get_json()
    message = sanitize_string(data['message'])

    return jsonify({
        'data': {
            'message': message,
            'response': 'This is a dummy response from the chatbot.'
        }
    }), 200
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from utils.utility import validate_request_params, sanitize_string
from utils.jwt import require_token
from utils.message_analyzer import analyze_text_words

import random

message_analyzer_v1_bp = Blueprint('message_analyzer_v1_bp', __name__, url_prefix='/v1/message_analyzer')

@message_analyzer_v1_bp.route('/analyze', methods=['POST'])
@require_token
def get_response_from_chatbot():
    if not request.is_json:
        raise BadRequest('Request must be JSON')
    
    is_valid, error_response = validate_request_params(request, ['message'])
    if not is_valid:
        raise BadRequest(error_response)

    data = request.get_json()
    message = sanitize_string(data['message'])

    analysis = analyze_text_words(message)

    score = random.randint(0, 100)
    
    return jsonify({
        'data': {
            'original_message': message,
            'score': score,
            'analysis': analysis
        }
    }), 200
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from utils.utility import validate_request_params, sanitize_string
from utils.jwt import require_token
from utils.message_analyzer import analyze_text_words, predict_cyberbullying

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

    results = predict_cyberbullying(message)

    score = int(results[0]['risk_score'] * 100)

    response_recipient = 'This is what you see if you are the recipient. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'
    response_sender = 'This is what you see if you are the sender. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'
    
    return jsonify({
        'data': {
            'original_message': message,
            'score': score,
            'analysis': analysis,
            'results': results,
            'response': {
                'recipient': response_recipient,
                'sender': response_sender
            }
        }
    }), 200
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from utils.utility import validate_request_params, sanitize_string
from utils.jwt import require_token
from utils.chatbot import get_bot_response

chatbot_v1_bp = Blueprint('chatbot_v1_bp', __name__, url_prefix='/v1/chatbot')

@chatbot_v1_bp.route('/get_response_from_chatbot', methods=['POST'])
@require_token
def get_response_from_chatbot():
    if not request.is_json:
        raise BadRequest('Request must be JSON')
    
    is_valid, error_response = validate_request_params(request, ['message'])
    if not is_valid:
        raise BadRequest(error_response)

    data = request.get_json()
    message = sanitize_string(data['message'])

    # get response from the chatbot
    bot_reply = get_bot_response(message)

    return jsonify({
        'data': {
            'message': message,
            'response': bot_reply
        }
    }), 200
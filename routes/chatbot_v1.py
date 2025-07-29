from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from utils.utility import validate_request_params, sanitize_string
from utils.jwt import require_token
import time

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

    # simulate working
    time.sleep(2)

    return jsonify({
        'data': {
            'message': message,
            'response': 'This is a dummy response from the chatbot.'
        }
    }), 200
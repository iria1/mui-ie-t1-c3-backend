from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from utils.utility import validate_request_params, sanitize_string
from utils.jwt import require_token
from utils.chatbot import get_bot_response
from utils.config import JWT_SECRET
import hmac
import hashlib
import secrets

chatbot_v1_bp = Blueprint('chatbot_v1_bp', __name__, url_prefix='/v1/chatbot')

@chatbot_v1_bp.route('/get_response_from_chatbot', methods=['POST'])
@require_token
def get_response_from_chatbot():
    if not request.is_json:
        raise BadRequest('Request must be JSON')
    
    is_valid, error_response = validate_request_params(request, ['message', 'token'])
    if not is_valid:
        raise BadRequest(error_response)

    data = request.get_json()
    message = sanitize_string(data['message'])

    result, session_id = verify(data['token'])

    if not result:
        raise BadRequest('Bad token')

    # get response from the chatbot
    bot_reply = get_bot_response(message, session_id)

    return jsonify({
        'data': {
            'message': message,
            'response': bot_reply
        }
    }), 200

@chatbot_v1_bp.route('/get_session_token', methods=['GET'])
@require_token
def get_session_token():
    session_id = secrets.token_hex(16)

    tag = hmac.new(JWT_SECRET.encode('UTF-8'), session_id.encode(), hashlib.sha256).hexdigest()
    
    return jsonify({
        'data': {
            'token': f'{session_id}.{tag}'
        }
    }), 200

@chatbot_v1_bp.route('/get_init_message', methods=['GET'])
@require_token
def get_init_message():
    # return a list of messages that the chatbot will write first
    return jsonify({
        'data': [
            'Hello, I\'m Caro! Ask me anything about cyberbullying!',
            'To start with, here are some questions you can ask me about cyberbullying:\n* What is cyberbullying, and how is it different from regular bullying?\n* What are some examples of cyberbullying?\n* Why is cyberbullying harmful?\n* How can I help a friend who is being cyberbullied?\n* What should I do if I\'m being bullied online?\n* How can I stay safe online and protect my privacy?\n* What does it mean to be an upstander in a cyberbullying situation?\n\nFeel free to ask any of these questions or anything else related to cyberbullying!',
            'By the way, I only talk about cyberbullying (that\'s my special mission!)'
        ]
    }), 200

def verify(token):
    try:
        session_id, tag = token.split('.')
    except ValueError:
        return False, None
    
    expected_tag = hmac.new(JWT_SECRET.encode('UTF-8'), session_id.encode(), hashlib.sha256).hexdigest()
    
    result = hmac.compare_digest(expected_tag, tag)

    if result:
        return result, session_id
    else:
        return result, None
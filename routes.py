import logging
from flask import request, jsonify
from app import app
from utils import validate_request_params, format_error_response, sanitize_string
#from api_client import AirVisualClient
#from config import MAX_CITIES_PER_REQUEST

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """API root endpoint with basic information"""
    return jsonify({
        "name": "ChildCyberCare API",
        "version": "1.0.0",
        "description": "REST API for C3 App",
        "endpoints": {
            "GET /": "List endpoints"
        }
    })

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify(format_error_response("The requested endpoint does not exist")), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors"""
    return jsonify(format_error_response("Method not allowed for this endpoint")), 405

@app.errorhandler(500)
def server_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify(format_error_response("Internal server error")), 500
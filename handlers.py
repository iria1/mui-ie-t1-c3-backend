from flask import jsonify
from utils import format_error_response
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
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
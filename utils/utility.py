import logging

logger = logging.getLogger(__name__)

def format_error_response(message, error_code=None):
    """
    Format standardized error response
    
    Args:
        message: Error message
        error_code: Optional error code
        
    Returns:
        Dictionary with error information
    """
    error_data = {
        "status": "error",
        "message": message
    }
    
    if error_code:
        error_data["error_code"] = error_code
        
    return error_data

def validate_request_params(request, required_params):
    """
    Validate that required parameters exist in the request
    
    Args:
        request: Flask request object
        required_params: List of required parameter names
        
    Returns:
        (is_valid, error_response) tuple where is_valid is boolean
        and error_response is the error message if validation fails
    """
    missing_params = []
    
    # Check for JSON request data
    if request.is_json:
        data = request.get_json()
        for param in required_params:
            if param not in data or not data[param]:
                missing_params.append(param)
    # Check URL parameters
    else:
        for param in required_params:
            if param not in request.args or not request.args.get(param):
                missing_params.append(param)
    
    if missing_params:
        error_msg = f"Missing required parameters: {', '.join(missing_params)}"
        logger.warning(error_msg)
        return False, error_msg
        
    return True, None

def sanitize_string(value):
    """
    Basic sanitization for string inputs
    
    Args:
        value: String to sanitize
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
        
    # Replace potentially problematic characters
    return value.strip()

import os
import logging
from flask import Flask
from flask_cors import CORS

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-key")

# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

# Configure logging
logger = logging.getLogger(__name__)

# Import routes after app is created to avoid circular imports
from routes import *

logger.info("Flask API initialized")

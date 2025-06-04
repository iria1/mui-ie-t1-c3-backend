import os
import logging
from flask import Flask
from flask_cors import CORS
from models import db
from flask_migrate import Migrate

# Create the Flask application
app = Flask(__name__)
#app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-key")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("MYSQL_CONN_STR", "")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

# Configure logging
logger = logging.getLogger(__name__)

# Import routes after app is created to avoid circular imports
from routes import *

logger.info("Flask API initialized")

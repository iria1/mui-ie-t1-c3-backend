import os
import logging
from flask import Flask
from flask_cors import CORS
from models import *
from flask_migrate import Migrate
from db import db
from handlers import register_error_handlers
from routes import api_bp

# Create the Flask application
app = Flask(__name__)
#app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-key")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("MYSQL_CONN_STR", "")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

ENV = os.environ.get("FLASK_ENV", "prod")

if ENV == 'dev':
    CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})
else:
    CORS(app, resources={r"/*": {"origins": "https://childcybercare.duckdns.org", "supports_credentials": True}})

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    #filename='c3app.log',
    #filemode='a',
    #format='%(asctime)s %(levelname)s %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routes
app.register_blueprint(api_bp)
register_error_handlers(app)

logger.info("Flask API initialized")

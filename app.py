import logging
from flask import Flask
from flask_cors import CORS
from models import *
from flask_migrate import Migrate
from utils.config import MYSQL_CONN_STR, ENV, APP_URL
from utils.db import db
from utils.error_handler import register_error_handlers
from routes import api_bp

# Create the Flask application
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = MYSQL_CONN_STR
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

if ENV == 'dev':
    CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})
else:
    CORS(app, resources={r"/*": {"origins": APP_URL, "supports_credentials": True}})

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

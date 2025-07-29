import os
from datetime import timedelta

# app environment
ENV = os.getenv("FLASK_ENV", "prod")
APP_URL = os.getenv("APP_URL", "https://childcybercare.duckdns.org")

# jwt config
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey")
JWT_EXPIRY = timedelta(days=30)

# mysql config
MYSQL_CONN_STR = os.getenv("MYSQL_CONN_STR", "")

# auth
SECRET_PASSWORD = os.getenv("SECRET_PASSWORD", "changeme")
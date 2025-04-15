import sys
from pathlib import Path
from flask import Flask, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Create Flask app
app = Flask(__name__, template_folder="../templates", static_folder="../static")

# Database configuration - using SQLite in memory for Vercel
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
from backend.models import db
db.init_app(app)

# Create tables - important for in-memory SQLite
with app.app_context():
    db.create_all()

# Import controllers AFTER app creation
from backend.controllers import *

# Vercel requires this specific WSGI setup
application = DispatcherMiddleware(app)

def handler(event, context):
    return application(event['path'], {
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'wsgi.input': event.get('body', '')
    })
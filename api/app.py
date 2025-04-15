import sys
from pathlib import Path
from flask import Flask, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Create Flask app
app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
from backend.models import db
db.init_app(app)

# Import controllers AFTER app creation
from backend.controllers import *

# Test route
@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Server is running"})

# Vercel requires this specific WSGI setup
application = DispatcherMiddleware(app)

def handler(event, context):
    return application(event['path'], {
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'wsgi.input': event.get('body', '')
    })
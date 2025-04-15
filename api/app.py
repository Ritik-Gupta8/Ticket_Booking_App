import sys
import os
from pathlib import Path
from flask import Flask, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Set the correct paths for Vercel
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

app = Flask(__name__, 
           template_folder=str(BASE_DIR / "templates"),
           static_folder=str(BASE_DIR / "static"))

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
from backend.models import db
db.init_app(app)

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")

# Import controllers AFTER app creation
try:
    from backend.controllers import *
    print("Controllers imported successfully")
except Exception as e:
    print(f"Error importing controllers: {str(e)}")

# Simple test route
@app.route('/test')
def test():
    return jsonify({"status": "ok", "message": "Test route works"})

# Vercel handler
application = DispatcherMiddleware(app)

def handler(event, context):
    print("Incoming request:", event['path'])
    return application(event['path'], {
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'wsgi.input': event.get('body', '')
    })
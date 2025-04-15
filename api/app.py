from flask import Flask, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from backend.models import db
db.init_app(app)

# Import controllers after app creation
from backend.controllers import *

# Test route
@app.route('/')
def home():
    return jsonify({"status": "success", "message": "Flask on Vercel"})

# Vercel requires this
app.wsgi_app = ProxyFix(app.wsgi_app)
application = DispatcherMiddleware(app)

def handler(event, context):
    return application(event, context)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
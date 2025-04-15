from app import app
from flask import jsonify

@app.route('/')
def home():
    return jsonify({"status": "OK", "message": "Flask app running on Vercel"})

# Vercel requires this
def handler(event, context):
    return app(event, context)
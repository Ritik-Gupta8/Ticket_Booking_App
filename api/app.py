from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "ok"})

def handler(event, context):
    return app(event, context)
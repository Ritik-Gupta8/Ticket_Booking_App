import sys
from pathlib import Path
from flask import Flask

# Set absolute paths
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

app = Flask(__name__)

# Basic test route
@app.route('/health')
def health_check():
    return {"status": "ok"}

# Vercel handler
def handler(event, context):
    return app({
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'wsgi.input': event.get('body', '')
    }, lambda status, headers: None)
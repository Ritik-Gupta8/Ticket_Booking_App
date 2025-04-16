# api/app.py

from flask import Flask
# api/app.py

from app import app as application  # Import the existing Flask app from root and expose it as `application`


app = Flask(__name__)

@app.route('/')
def hello():
    return 'Flask on Vercel!'

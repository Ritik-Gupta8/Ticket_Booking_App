# api/app.py

from flask import Flask
from app import app

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Flask on Vercel!'

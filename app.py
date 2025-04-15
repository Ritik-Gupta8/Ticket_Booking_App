from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Temporary solution
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import your routes after app creation
from backend.controllers import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
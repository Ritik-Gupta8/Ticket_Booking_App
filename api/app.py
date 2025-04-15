import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask
from backend.models import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
db.init_app(app)

# Import controllers after app creation
from backend.controllers import *

def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run()
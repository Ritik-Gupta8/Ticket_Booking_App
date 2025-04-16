import os
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'

from flask import Flask
from backend.models import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ticket_show.sqlite3"
app.debug = True

# Initialize DB
db.init_app(app)

# Import controllers after app creation
with app.app_context():
    from backend.controllers import register_routes
    register_routes(app)
    db.create_all()

print("Ticket show app is started!")

if __name__ == "__main__":
    app.run()
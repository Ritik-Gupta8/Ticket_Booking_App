import os
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'  # Set writable cache dir

from flask import Flask
from backend.models import db

# Initialize Flask app first
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ticket_show.sqlite3"
app.debug = True

# Initialize DB
db.init_app(app)

# Import controllers AFTER app is created
with app.app_context():
    from backend.controllers import register_routes
    register_routes(app)  # Explicitly pass app to controllers
    db.create_all()

print("Ticket show app is started!")

# Vercel handler
def handler(request):
    with app.app_context():
        return app(request)

if __name__ == "__main__":
    with app.app_context():
        app.run()
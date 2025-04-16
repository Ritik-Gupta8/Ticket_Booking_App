from flask import Flask
from backend.models import db
from backend.controllers import *  # Import routes

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ticket_show.sqlite3"
app.debug = True

# Initialize DB
db.init_app(app)
with app.app_context():
    db.create_all()

print("Ticket show app is started..")

# Vercel handler
def handler(request):
    with app.app_context():
        return app(request)

if __name__ == "__main__":
    app.run()
# api/app.py
from app import app  # Import your main Flask app from root

# Vercel requires a WSGI handler
def handler(request):
    with app.app_context():
        return app(request)

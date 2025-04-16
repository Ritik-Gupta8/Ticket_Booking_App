from app import app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Vercel-compatible WSGI application
application = DispatcherMiddleware(app)

def handler(event, context):
    with app.app_context():
        return application(event, context)
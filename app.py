#Starting of the application
from flask import Flask
from backend.models import db
from backend.api_controllers import *


app=None

def setup_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///ticket_show.sqlite3" #Having db file
    db.init_app(app) #Flask app connected to db 
    # api.init_app(app) #Flask app coonect to apis
    app.app_context().push() # Direct access to other modules
    app.debug=True
    print("Ticker show app is started..")

#call th funnction
setup_app()  
#helo
from backend.controllers import *

@app.route("/ping")
def ping():
    return "Flask app is working!"

# Required for Vercel
def handler(environ, start_response):
    return app(environ, start_response)

if __name__ =="__main__":
    app.run()
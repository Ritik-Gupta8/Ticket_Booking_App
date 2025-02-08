#Starting of the application
from flask import Flask
from backend.models import db

app=None

def setup_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///ticket_show.sqlite3" #Having db file
    db.init_app(app) #Flask app connected to db 
    app.app_context().push() # Direct access to other modules
    app.debug=True
    print("Ticker show app is started..")

#call th funnction
setup_app()

from backend.controllers import *

if __name__ =="__main__":
    app.run()
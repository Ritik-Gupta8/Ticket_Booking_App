# app_route
from flask import Flask,render_template,request,url_for,redirect
from .models import *
from flask import current_app as app
from datetime import datetime



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        usr=User_Info.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0: #Existed and admin
            return redirect(url_for("admin_dashboard",name=uname))
        elif usr and usr.role==1: #Existed and user
            return redirect(url_for("user_dashboard",name=uname))
        else:
            return render_template("login.html",msg="Invalid user credentials...")


    return render_template("login.html",msg="")

@app.route("/register",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        full_name=request.form.get("full_name")
        address=request.form.get("location")
        pincode=request.form.get("pincode")
    
        if not uname or not pwd or not full_name or not address or not pincode:
            return render_template("signup.html", msg="All fields are required!")    
        usr=User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html",msg="Sorry , this mail is already registered!!!")

        new_usr=User_Info(email=uname,password=pwd,full_name=full_name,address=address,pincode=pincode)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Thaknyou for registration, Try login now...")

    return render_template("signup.html",msg="")

#common route for admin
@app.route("/admin/<name>")
def admin_dashboard(name):
    theatres=get_theatres()
    return render_template("admin_dashboard.html",name=name,theatres=theatres)

#common route for user
@app.route("/user/<name>")
def user_dashboard(name):
    return render_template("user_dashboard.html",name=name)



@app.route("/venue/<name>",methods=["POST","GET"])
def add_venue(name):
    if request.method=="POST":
        vname=request.form.get("name")
        location=request.form.get("location")
        pincode=request.form.get("pincode")
        capacity=request.form.get("capacity")
        new_theatre=Theatre(name=vname,location=location,pincode=pincode,capacity=capacity)
        db.session.add(new_theatre)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))

    return render_template("add_venue.html",name=name)

@app.route("/show/<venue_id>/<name>",methods=["POST","GET"])
def add_show(venue_id,name):
    if request.method=="POST":
        sname=request.form.get("name")
        tags=request.form.get("tags")
        tkt_price=request.form.get("tkt_price")
        dt_time=request.form.get("date_time") # data is in stirng foramt
        
        #processing date and time 
        date_time=datetime.strptime(dt_time,"%Y-%m-%dT%H:%M")
        new_show=Show(name=sname,tags=tags,tkt_price=tkt_price,date_time=date_time,theatre_id=venue_id)
        db.session.add(new_show)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))

    return render_template("add_show.html",venue_id=venue_id,nmae=name)

@app.route("/search/<name>",methods=["GET","POST"])
def search(name):
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        by_venue=search_by_venue(search_txt)
        by_location=search_by_location(search_txt)
        if by_venue:
            return render_template("admin_dashboard.html",name=name,theatres=by_venue)
        elif by_location:
            return render_template("admin_dashboard.html",name=name,theatres=by_location)


    return redirect(url_for("admin_dashboard",name=name))

#Other supportedd function
def get_theatres():
    theatres=Theatre.query.all()
    return theatres

def search_by_venue(search_txt):
    theatres=Theatre.query.filter(Theatre.name.ilike(f"%{search_txt}%")).all()
    return theatres

def search_by_location(search_txt):
    theatres=Theatre.query.filter(Theatre.location.ilike(f"%{search_txt}%")).all()
    return theatres
# app_route
from flask import Flask,render_template,request,url_for,redirect
from .models import *
from flask import current_app as app
from datetime import datetime
from sqlalchemy import func 



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
            return redirect(url_for("user_dashboard",name=uname,id=usr.id))
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
@app.route("/user/<id>/<name>")
def user_dashboard(id,name):
    theatres=get_theatres()
    dt_time_now=datetime.today().strftime("%Y-%m-%dT%H:%M")
    dt_time_now=datetime.strptime(dt_time_now,"%Y-%m-%dT%H:%M")

    return render_template("user_dashboard.html",uid=id,name=name,theatres=theatres,dt_time_now=dt_time_now)



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

    return render_template("add_show.html",venue_id=venue_id,name=name)

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

@app.route("/edit_venue/<id>/<name>",methods=["GET","POST"])
def edit_venue(id,name):
    v=get_venue(id)
    if request.method=="POST":
        tname=request.form.get("tname")
        location=request.form.get("location")
        pincode=request.form.get("pincode")
        capacity=request.form.get("capacity")
        v.name=tname
        v.location=location
        v.pincode=pincode
        v.capacity=capacity
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    
    return render_template("edit_venue.html",venue=v,name=name)

@app.route("/delete_venue/<id>/<name>",methods=["GET","POST"])
def delete_venue(id,name):
    v=get_venue(id)
    db.session.delete(v)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))

@app.route("/edit_show/<id>/<name>",methods=["GET","POST"])
def edit_show(id,name):
    s=get_show(id)
    if request.method=="POST":
        sname=request.form.get("sname")
        tags=request.form.get("tags")
        tkt_price=request.form.get("tkt_price")
        date_time=request.form.get("date_time") # data is in stirng foramt
        date_time=datetime.strptime(date_time,"%Y-%m-%dT%H:%M")
        s.name=sname
        s.tags=tags
        s.tkt_price=tkt_price
        s.date_time=date_time
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    
    return render_template("edit_show.html",show=s,name=name)

@app.route("/delete_show/<id>/<name>",methods=["GET","POST"])
def delete_show(id,name):
    s=get_show(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))

@app.route("/book_ticket/<uid>/<sid>/<name>",methods=["GET","POST"])
def book_ticket(uid,sid,name):
    if request.method=="POST":
        no_of_tickets=request.form.get("no_of_tickets")
        new_ticket=Ticket(no_of_tickets=no_of_tickets,sl_no_tickets="",user_id=uid,show_id=sid)
        db.session.add(new_ticket)
        db.session.commit()
        return redirect(url_for("user_dashboard",id=uid,name=name))

    # Get method is execueted
    show=Show.query.filter_by(id=sid).first()
    theatre=Theatre.query.filter_by(id=show.theatre_id).first()
    available_seats=theatre.capacity
    # Booked Tickets by aggregate functions sum
    book_tickets=Ticket.query.with_entities(func.sum(Ticket.no_of_tickets)).group_by(Ticket.show_id).filter_by(show_id=sid).first()
    if book_tickets:
        available_seats -= book_tickets[0]

    return render_template("book_ticket.html",uid=uid,sid=sid,name=name,tname=theatre.name,sname=show.name,available_seats=available_seats,tktprice=show.tkt_price)

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

def get_venue(id):
    theatre=Theatre.query.filter_by(id=id).first()
    return theatre

def get_show(id):
    show=Show.query.filter_by(id=id).first()
    return show
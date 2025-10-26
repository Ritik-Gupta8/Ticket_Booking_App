# app_route
from flask import Flask,render_template,request,url_for,redirect
from .models import *
from flask import current_app as app
from datetime import datetime
from sqlalchemy import func 
from werkzeug.utils import secure_filename


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
            return render_template("login.html",msg="Incorrect username or password!!!")
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


@app.route("/venue/<name>",methods=["POST","GET"])
def add_venue(name):
    if request.method=="POST":
        vname=request.form.get("name")
        location=request.form.get("location")
        pincode=request.form.get("pincode")
        capacity=request.form.get("capacity")
        file=request.files["file_upload"]
        url=""
        if file.filename:
            file_name=secure_filename(file.filename) # verification of the file is done
            url='./uploaded_files/' +vname+"_"+file_name
            file.save(url)
        new_theatre=Theatre(name=vname,location=location,pincode=pincode,capacity=capacity,venue_pic_url=url)
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

@app.route("/search_admin/<name>",methods=["GET","POST"])
def search_admin(name):
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

@app.route("/user_details/<name>")
def admin_users(name):
    users = User_Info.query.filter_by(role=1).order_by(User_Info.total_spent.desc()).all()
    return render_template("user_details.html", name=name, users=users)

@app.route("/admin_summary/<name>")
def admin_summary(name):
    theatres = Theatre.query.all()  # or your get_theatres()
    theatre_names = [t.name for t in theatres]
    theatre_capacities = [t.capacity for t in theatres]
    theatre_revenues = [float(t.total_revenue or 0) for t in theatres]  # ✅ ensure numeric

    return render_template(
        "admin_summary.html",
        name=name,
        theatre_names=theatre_names,
        theatre_capacities=theatre_capacities,
        theatre_revenues=theatre_revenues
    )


#######################################################################################################################################################3

#common route for user
@app.route("/user/<id>/<name>")
def user_dashboard(id, name):
    user_info = User_Info.query.get_or_404(id)
    theatres = get_theatres()
    dt_time_now = datetime.today().strftime("%Y-%m-%dT%H:%M")
    dt_time_now = datetime.strptime(dt_time_now, "%Y-%m-%dT%H:%M")

    return render_template("user_dashboard.html", id=id, name=name, user_info=user_info, theatres=theatres, dt_time_now=dt_time_now)

@app.route("/search_user/<id>/<name>", methods=["GET", "POST"])
def search_user(id, name):
    user_info = User_Info.query.get_or_404(id)

    if request.method == "POST":
        search_txt = request.form.get("query")

        if not search_txt:
            return redirect(url_for("user_dashboard", id=id, name=name))

        # Search venue & location
        matched_theatres = Theatre.query.filter(
            (Theatre.name.ilike(f"%{search_txt}%")) |
            (Theatre.location.ilike(f"%{search_txt}%"))
        ).all()

        # Search by show name
        matched_shows = Show.query.filter(Show.name.ilike(f"%{search_txt}%")).all()

        dt_time_now = datetime.today().strftime("%Y-%m-%dT%H:%M")
        dt_time_now = datetime.strptime(dt_time_now, "%Y-%m-%dT%H:%M")

        # ✅ If theatres found → show theatres
        if matched_theatres:
            return render_template("user_dashboard.html", 
                                   id=id, name=name, 
                                   user_info=user_info, 
                                   theatres=matched_theatres,
                                   dt_time_now=dt_time_now)

        # ✅ If shows found → display theatres of those shows
        if matched_shows:
            # Extract theatres from shows
            theatre_ids = {show.theatre_id for show in matched_shows}
            theatres_for_shows = Theatre.query.filter(Theatre.id.in_(theatre_ids)).all()

            return render_template("user_dashboard.html", 
                                   id=id, name=name, 
                                   user_info=user_info, 
                                   theatres=theatres_for_shows,
                                   dt_time_now=dt_time_now,
                                   shows=matched_shows)

    return redirect(url_for("user_dashboard", id=id, name=name))


@app.route("/book_ticket/<id>/<sid>/<name>", methods=["GET", "POST"])
def book_ticket(id, sid, name):
    show = Show.query.get_or_404(sid)
    theatre = Theatre.query.get_or_404(show.theatre_id)
    user = User_Info.query.get_or_404(id)

    # Calculate available seats
    total_booked = db.session.query(func.sum(Ticket.no_of_tickets))\
        .filter(Ticket.show_id == sid).scalar() or 0
    available_seats = theatre.capacity - total_booked

    if request.method == "POST":
        no_of_tickets = int(request.form.get("no_of_tickets"))
        if no_of_tickets > available_seats:
            return render_template(
                "book_ticket.html",
                id=id, sid=sid, name=name,
                tname=theatre.name, sname=show.name,
                available_seats=available_seats,
                tktprice=show.tkt_price,
                error="Not enough seats available!",
                user_info=user )
        total_price = no_of_tickets * show.tkt_price
        new_ticket = Ticket(no_of_tickets=no_of_tickets,sl_no_tickets="",user_id=id,show_id=sid,total_cost=total_price)
        db.session.add(new_ticket)

        show.total_revenue = (show.total_revenue or 0) + total_price
        theatre.total_revenue = (theatre.total_revenue or 0) + total_price
        user.total_spent = (user.total_spent or 0) + total_price
        db.session.commit()
        return redirect(url_for("user_dashboard", id=id, name=name))

    return render_template("book_ticket.html",id=id, sid=sid, name=name,tname=theatre.name, sname=show.name,available_seats=available_seats,tktprice=show.tkt_price,
        user_info=user)


@app.route("/user_bookings/<id>/<name>")
def user_bookings(id, name):
    user = User_Info.query.get_or_404(id)
    tickets = Ticket.query.filter_by(user_id=user.id).order_by(Ticket.id.desc()).all()
    dt_time_now = datetime.now()

    return render_template("user_bookings.html",name=name,user_info=user,tickets=tickets,dt_time_now=dt_time_now)



@app.route("/user_summary/<int:id>/<name>")
def user_summary(id, name):
    user = User_Info.query.get_or_404(id)

    # 🎭 Spend per theatre
    theatre_spend = (
        db.session.query(Theatre.name, db.func.sum(Ticket.no_of_tickets * Show.tkt_price))
        .join(Show, Show.theatre_id == Theatre.id)
        .join(Ticket, Ticket.show_id == Show.id)
        .filter(Ticket.user_id == user.id)
        .group_by(Theatre.name)
        .all()
    )
    theatre_names = [t[0] for t in theatre_spend]
    spend_amounts = [float(t[1]) if t[1] else 0 for t in theatre_spend]

    # 🏙️ Spend per city (Theatre.location)
    city_spend = (
        db.session.query(Theatre.location, db.func.sum(Ticket.no_of_tickets * Show.tkt_price))
        .join(Show, Show.theatre_id == Theatre.id)
        .join(Ticket, Ticket.show_id == Show.id)
        .filter(Ticket.user_id == user.id)
        .group_by(Theatre.location)
        .all()
    )
    city_names = [c[0] for c in city_spend]
    city_amounts = [float(c[1]) if c[1] else 0 for c in city_spend]

    # 🧮 Total spend
    total_spent = sum(spend_amounts)

    return render_template(
        "user_summary.html",
        name=name,
        user_info=user,
        theatre_names=theatre_names,
        spend_amounts=spend_amounts,
        city_names=city_names,
        city_amounts=city_amounts,
        total_spent=total_spent
    )


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

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
def search_user(name, id):
    user_info = User_Info.query.get_or_404(id)

    if request.method == "POST":
        search_txt = request.form.get("query")  # Match input name from form

        if not search_txt:
            return redirect(url_for("user_dashboard", id=id, name=name))
        by_venue = search_by_venue(search_txt)
        by_location = search_by_location(search_txt)
        by_show = Show.query.filter(Show.name.ilike(f"%{search_txt}%")).all()
        if by_venue:
            return render_template("user_dashboard.html", id=id, name=name, user_info=user_info, theatres=by_venue)
        elif by_location:
            return render_template("user_dashboard.html", id=id, name=name, user_info=user_info, theatres=by_location)
        elif by_show:
            return render_template("user_dashboard.html", id=id, name=name, user_info=user_info, shows=by_show)

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


# @app.route("/admin_summary/<name>")
# def admin_summary(name):
#     get_theatres_summary()  # ✅ no need to store return value or call savefig again
#     return render_template('admin_summary.html', name = name)

# import os
# def get_theatres_summary():
#     theatres = get_theatres()
#     summary = {t.name: t.capacity for t in theatres}
#     x_names = list(summary.keys())
#     y_capacities = list(summary.values())

#     plt.figure(figsize=(8, 6))
#     plt.bar(x_names, y_capacities, color="blue", width=0.4)
#     plt.title("Theatres/Capacities")
#     plt.xlabel("Theatre")
#     plt.ylabel("Capacity")

#     # Make sure the folder exists
#     output_dir = os.path.join('static', 'images')
#     os.makedirs(output_dir, exist_ok=True)  # ✅ This prevents the FileNotFoundError

#     output_path = os.path.join(output_dir, 'theatre_summary.jpeg')
#     plt.savefig(output_path)
#     plt.close()

#     return output_path

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



@app.route("/user_summary/<name>")
def user_summary(name):
    user = User_Info.query.filter_by(full_name=name).first()

    if not user:
        return "User not found", 404

    # Aggregate total spend per theatre
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

    return render_template(
        "user_summary.html",
        name=name,
        theatre_names=theatre_names,
        spend_amounts=spend_amounts
    )

from flask import Blueprint, render_template, request, redirect, session, url_for
from flask_bcrypt import Bcrypt
from database.models import db, User, LoginLog

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth.route("/")
def home():
    return render_template("login.html", error=False)

@auth.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    ip_address = request.remote_addr
    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session["user"] = username
        # Log successful login
        log = LoginLog(username=username, ip_address=ip_address, status="success")
        db.session.add(log)
        db.session.commit()
        return redirect(url_for("dashboard.dashboard"))

    # Log failed login
    log = LoginLog(username=username, ip_address=ip_address, status="failed")
    db.session.add(log)
    db.session.commit()
    return render_template("login.html", error=True), 401

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        new_user = User(username=username, password=password, role="admin")
        db.session.add(new_user)
        db.session.commit()
        return "User created! <a href='/'>Login now</a>"
    return '''
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input type="password" name="password"><br>
            <button type="submit">Register</button>
        </form>
    '''

@auth.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.home"))

from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'cctv_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:joshevasco123@localhost/cctv_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='viewer')

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        session["user"] = username
        return redirect(url_for("dashboard"))
    return "Invalid credentials!", 401

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))
    return f"Welcome, {session['user']}! CCTV Dashboard"

@app.route("/register", methods=["GET", "POST"])
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
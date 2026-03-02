"""Docstring Health Bridge
A health tracker, specifically designed for the elderly.
Users can easily add their personal health info for doctors to find and read
Users can also set reminders for medicine or appointments
Elderly tend to find using technology difficult and are usually mobile users
So the app will be designed to use very simply and mobile friendly
By Miguel Monreal on 27/02/2026"""

from flask import (Flask, render_template,
                   url_for, redirect)
from flask_login import (login_required,
                         login_user)
from models import (User)
from forms import RegisterForm, LoginForm
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

# Initialises app
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Initialize the DB
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = ("sqlite:///healthbridge.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.config["SECRET_KEY"] = "secret_shhhh"


@app.route("/")
def home():
    return render_template("home.html", header="Home")


@login_required
@app.route("/dashboard")
def dashboard():
    return "Dashboard"


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    return render_template("login.html", header="Login",
                           form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("home"))

    return render_template("register.html", header="Register",
                           form=form)


if __name__ == "__main__":
    app.run(debug=True)

"""Docstring Health Bridge
A health tracker, specifically designed for the elderly.
Users can easily add their personal health info for doctors to easily find and read
Users can also set reminders for medicine or appointments
Elderly tend to find using technology difficult and are usually mobile users
So the app will be designed to use very simply and mobile friendly
By Miguel Monreal on 27/02/2026"""

from flask import Flask, render_template, url_for
from flask_login import (LoginManager, login_required)
from config import DB
from models import (User, Type, Health,
                    UserHealth)
import os

# Initialises app
app = Flask(__name__)

# Initialize the DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = ("sqlite:///healthbridge.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
DB.init_app(app)

app.config["SECRET_KEY"] = "secret_shhhh"


@app.route("/")
def home():
    return render_template("home.html", header="Home")


@login_required
@app.route("/dashboard")
def dashboard():
    return "Dashboard"


@app.route("/login")
def login():
    return render_template("login.html", header="Login")


@app.route("/register")
def register():
    return render_template("register.html", header="Register")


if __name__ == "__main__":
    app.run(debug=True)

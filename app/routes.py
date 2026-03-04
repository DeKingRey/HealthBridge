"""
Health Bridge
A mobile-friendly health tracking app designed specifically for the elderly

Features:
- Store personal Health info for doctors to access
- Set reminders for medicine and/or appointments
- Simple and accessible user interface for elderly users

Author: Miguel Monreal
Date: 27-02-2026
"""

from flask import (render_template, Blueprint, url_for,
                   redirect)
from flask_login import (login_required, login_user,
                         logout_user, current_user)
from app.models import (User)
from app.forms import RegisterForm, LoginForm
from app import db, bcrypt, login_manager

main = Blueprint("main", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main.route("/")
def home():
    return render_template("home.html", header="Home")


@main.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html", header="Dashboard")


@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    # Logs in user if validated, user is valid, and password matches user
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("main.dashboard"))

    return render_template("login.html", header="Login",
                           form=form)


@main.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    # Adds user to database if validated successfully
    if form.validate_on_submit():
        # Generates a secure password
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("main.home"))

    return render_template("register.html", header="Register",
                           form=form)

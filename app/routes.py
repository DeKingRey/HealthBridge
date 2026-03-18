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
                   redirect, request)
from flask_login import (login_required, login_user, logout_user,
                         current_user)
from app.models import (User)
from app.forms import RegisterForm, LoginForm, ResetPasswordForm
from app import db, bcrypt, login_manager, mail
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
import os

main = Blueprint("main", __name__)
serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))


def generate_verification_token(email):
    return serializer.dumps(email, salt="email-confirm")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@main.route("/")
def home():
    return render_template("home.html", header="Home")


@main.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html", header="Dashboard")


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    # Logs in user if verified, user is valid, and password matches user
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                remember_flag = request.form.get("remember") == "True"
                if user.is_verified:
                    login_user(user, remember=remember_flag)
                    return redirect(url_for("main.dashboard"))
                else:
                    subject, body = register_email_info(user.email,
                                                        remember_flag)
                    send_verification_email(user.email, subject, body)
                    return render_template("verify_email.html",
                                           header="Please verify your email")
    return render_template("login.html", header="Login",
                           form=form)


@main.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()

    # Adds user to database if validated successfully
    if form.validate_on_submit():
        # Generates a secure password
        hashed_password = bcrypt.generate_password_hash(form.password.data)

        new_user = User(username=form.username.data, email=form.email.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        remember_flag = request.form.get("remember") == "True"

        # Sends verification email
        subject, body = register_email_info(form.email.data, remember_flag)
        send_verification_email(form.email.data, subject, body)
        return render_template("verify_email.html",
                               header="Please verify your email")
    return render_template("register.html", header="Register",
                           form=form)


@main.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordForm()
    email_verified = request.args.get("email_verified", "False") == "True"
    email = request.args.get("email")

    # Send email to user to verify email then allows for password reset
    if form.validate_on_submit():
        if not email_verified:
            token = generate_verification_token(form.email.data)
            verify_url = url_for("main.verify_email",
                                 token=token,
                                 forgot_password=True,
                                 register=False,
                                 _external=True)

            subject = "Reset Password Request"
            body = f"""
            Click on the link to reset your password:

            {verify_url}
            """
            send_verification_email(form.email.data, subject, body)
        elif email_verified:
            # Generates a secure password
            hashed_password = bcrypt.generate_password_hash(form.password.data)

            user = User.query.filter_by(email=email).first()
            # Updates password
            if user:
                user.password = hashed_password
                db.session.commit()
                remember_flag = request.form.get("remember") == "True"
                login_user(user, remember=remember_flag)
                return redirect(url_for("main.dashboard"))
            return redirect(url_for("main.login"))
    return render_template("reset-password.html", header="Reset Password",
                           form=form, email_verified=email_verified)


@main.route("/verify/<token>")
def verify_email(token):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=3600)
    except ValueError:
        return "Verification link expired or invalid"

    forgot_password = request.args.get("forgot_password", "False") == "True"
    register = request.args.get("register", "False") == "True"
    user = User.query.filter_by(email=email).first()

    if user:
        if register:
            user.is_verified = True
            db.session.commit()

            remember_flag = request.args.get("remember", "False") == "True"
            login_user(user, remember=remember_flag)
            return redirect(url_for("main.dashboard"))
        elif forgot_password:
            return redirect(url_for("main.reset_password",
                                    email_verified=True,
                                    email=email))
    return redirect(url_for("main.login"))


def send_verification_email(email, subject, body):
    # Send a verification email to the user
    subject = subject
    msg = Message(subject=subject,
                  recipients=[email]
                  )

    msg.body = body
    mail.send(msg)


def register_email_info(email, remember_flag):
    token = generate_verification_token(email)
    verify_url = url_for("main.verify_email",
                         token=token,
                         forgot_password=False,
                         register=True,
                         _external=True,
                         remember=remember_flag)

    subject = "Please verify your email"
    body = f"""
    Welcome!

    Click the link below to verify your account:

    {verify_url}
    """
    return subject, body

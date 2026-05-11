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
                   redirect, request, make_response)
from flask_login import (login_required, login_user, logout_user,
                         current_user)
from app.models import (User, Health, UserHealth, HealthType,
                        Reminder, ReminderType)
from app.forms import (RegisterForm, LoginForm, ResetPasswordForm,
                       AddHealthInfoForm, AddReminderForm)
from app import db, bcrypt, login_manager, mail
from app.tasks import send_reminder_email
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from weasyprint import HTML
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta, timezone
from config import (APPOINTMENT_ID, MEDICATION_ID)
import os

main = Blueprint("main", __name__)
serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))


def generate_verification_token(email):
    return serializer.dumps(email, salt="email-confirm")


def confirm_verification_token(token, expiration=3600):
    try:
        email = serializer.loads(
            token,
            salt="email-confirm",
            max_age=expiration
        )
    except Exception:
        return None
    return email


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


@main.route("/health-info", methods=["GET", "POST"])
@login_required
def health_info():
    # Gets only the types that the user has in their health records
    # This is to simplify the display
    types = get_type_info(True)
    user_health_entries = get_user_health_entries()
    return render_template("health-info.html", header="Health Info",
                           types=types,
                           user_health_entries=user_health_entries)


@main.route("/add-health-info", methods=["GET", "POST"])
@login_required
def add_health_info():
    form = AddHealthInfoForm()

    # Gets public health info
    health_records = Health.query.filter_by(is_public=True).all()
    search_content = [
        {"id": h.id, "name": h.name,
         "desc": h.default_description,
         "type_id": h.type_id}
        for h in health_records
    ]

    # Populates type choices
    types = get_type_info()
    form.type_id.choices = [(-1, "Select a type")] + [(t.id, t.name)
                                                      for t in types]

    # Adds info to database if validated succesfully
    if form.validate_on_submit():
        existing_info = request.form.get("existing_info") == "True"

        # Adds input as new info if it doesn't exist
        if not existing_info:
            is_public = current_user.is_admin

            health_info = Health(name=form.name.data,
                                 default_description=form.default_desc.data,
                                 type_id=form.type_id.data,
                                 is_public=is_public)
            db.session.add(health_info)
            db.session.commit()
        # Adds existing info if search was used
        else:
            # Checks that existing info id is in database
            health_info_id = request.form.get("health_info_id")

            try:
                health_info_id = int(health_info_id)
            except (TypeError, ValueError):
                form.name.errors.append("Invalid ID")
                return render_template("add-health-info.html",
                                       header="Add Health Info",
                                       form=form,
                                       search_content=search_content)
            health_info_ids = [h.id for h in health_records]

            # If the id does not exist, it returns an error
            if health_info_id not in health_info_ids:
                form.name.errors.append("Invalid ID")
                return render_template("add-health-info.html",
                                       header="Add Health Info",
                                       form=form,
                                       search_content=search_content)
            health_info = Health.query.filter_by(id=health_info_id).first()
        # Adds new health info
        new_user_health_info = UserHealth(user_id=current_user.id,
                                          health_id=health_info.id,
                                          description=health_info.default_description)
        db.session.add(new_user_health_info)
        db.session.commit()

        return redirect(url_for("main.health_info"))
    return render_template("add-health-info.html", header="Add Health Info",
                           form=form, search_content=search_content)


@main.route("/remove-health-info", methods=["GET", "POST"])
def remove_health_info():
    entry_id = request.form.get("entry_id")

    # First ensures that the entry exists and belongs to the user
    user_health_entry = UserHealth.query.get(entry_id)
    if not user_health_entry:
        return "Not found", 404

    if user_health_entry.user_id != current_user.id:
        return "Unauthorized", 403

    # Deletes user health entry
    db.session.delete(user_health_entry)
    db.session.commit()
    return redirect(url_for("main.health_info"))


@main.route("/send-health-info", methods=["POST"])
def send_health_info():
    email = request.form.get("receiver_email")

    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError:
        return render_template("email-sent.html",
                               header="Invalid Email Address",
                               message="The email you inputted was invalid",
                               email_failed=True)

    user_info = User.query.get(current_user.id)
    subject = f"Health Info for {user_info.username}"
    body = f"Attached is all health information for {user_info.username}."
    pdf = generate_health_pdf(user_info)

    send_email(email, subject, body, attachments=[("patient_summary.pdf",
                                                   "application/pdf", pdf)])

    return redirect(url_for("main.health_info"))


@main.route("/download-health-pdf")
def download_health_pdf():
    user_info = User.query.get(current_user.id)
    pdf = generate_health_pdf(user_info)

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = """attachment;
                                                filename=patient_summary.pdf"""

    return response


def generate_health_pdf(user):
    types = get_type_info(True)
    user_health_entries = get_user_health_entries()

    data = {
        "name": user.username,
        "dob": "placeholder dob",
        "types": types,
        "user_health_entries": user_health_entries
    }

    html = render_template("health-pdf-template.html", **data)
    pdf = HTML(string=html).write_pdf()

    return pdf


@main.route("/reminders")
def reminders():
    return render_template("reminders.html", header="Reminders")


@main.route("/add-reminder", methods=["GET", "POST"])
@login_required
def add_reminder():
    form = AddReminderForm()

    # Populates type choices
    types = ReminderType.query.all()
    form.type_id.choices = [(-1, "Select a type")] + [(t.id, t.name)
                                                      for t in types]

    # Adds info to database if validated succesfully
    if form.validate_on_submit():
        local_tz = datetime.now().astimezone().tzinfo

        # Appointment Reminder
        if form.type_id.data == APPOINTMENT_ID:
            scheduled_time = form.appointment_datetime.data.replace(
                tzinfo=local_tz)
            # Converts to UTC for scheduling
            scheduled_time = scheduled_time.astimezone(timezone.utc)

        # Medication Reminder
        elif form.type_id.data == MEDICATION_ID:
            med_time = form.medication_time.data
            scheduled_time = datetime.combine(datetime.today().date(),
                                              med_time, tzinfo=local_tz)
            # Converts to UTC for scheduling
            scheduled_time = scheduled_time.astimezone(timezone.utc)

            # Schedules for tomorrow if time has already passed
            if scheduled_time < datetime.now(timezone.utc):
                scheduled_time += timedelta(days=1)

        reminder = Reminder(user_id=current_user.id,
                            name=form.name.data,
                            description=form.desc.data,
                            type_id=form.type_id.data,
                            scheduled_time=scheduled_time)
        db.session.add(reminder)
        db.session.commit()

        # TEST - TEMPORARY REMMEBER TO DELETE
        send_reminder_email.apply_async(
            args=[
                current_user.email,
                form.name.data,
                form.desc.data,
                
            ],
            eta=scheduled_time
        )

        return redirect(url_for("main.reminders"))
    return render_template("add-reminder.html", header="Add Reminder",
                           form=form)


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
                    send_email(user.email, subject, body)

                    message = "Please check your emails to verify your account"
                    return render_template("email-sent.html",
                                           header="Please verify your email",
                                           message=message, email_failed=False)
            else:
                form.password.errors.append("Password is incorrect")
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
        send_email(form.email.data, subject, body)

        message = "Please check your emails to verify your account"
        return render_template("email-sent.html",
                               header="Please verify your email",
                               message=message, email_failed=False)
    return render_template("register.html", header="Register",
                           form=form)


@main.route("/reset-password", methods=["GET", "POST"])
def reset_password_request():
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_verification_token(user.email)

            reset_url = url_for(
                "main.reset_password",
                token=token,
                forgot_password=True,
                register=False,
                _external=True
            )

            send_email(
                user.email,
                "Reset Password Request",
                f"Click to reset: {reset_url}"
            )
        message = "Please check your emails to reset your password"
        return render_template("email-sent.html",
                               header="Reset Password",
                               message=message, email_failed=False)
    return render_template("reset-password.html", form=form,
                           email_verified=False)


@main.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()

    email = confirm_verification_token(token)
    if not email:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for("main.login"))

    # Send email to user to verify email then allows for password reset
    if form.validate_on_submit():
        # Generates a secure password and updates it
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()

        login_user(user)
        return redirect(url_for("main.dashboard"))
    return render_template("reset-password.html", header="Reset Password",
                           form=form, email_verified=True)


@main.route("/verify/<token>")
def verify_email(token):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=3600)
    except ValueError:
        return "Verification link expired or invalid"

    register = request.args.get("register", "False") == "True"
    user = User.query.filter_by(email=email).first()

    if user:
        if register:
            user.is_verified = True
            db.session.commit()

            remember_flag = request.args.get("remember", "False") == "True"
            login_user(user, remember=remember_flag)
            return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


def send_email(email, subject, body, attachments=None):
    # Send an email to the specified email
    subject = subject
    msg = Message(subject=subject,
                  recipients=[email]
                  )

    msg.body = body

    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)

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


def get_type_info(users_only=False):
    type_info = HealthType.query.all()

    # Will return only types that the user has in their health records
    if users_only:
        new_type_info = []

        # Gets the specific type ids from the health records of the user
        user_types = db.session.query(Health.type_id).join(UserHealth).filter(
            UserHealth.user_id == current_user.id
        ).all()

        user_types_ids = {t[0] for t in user_types}

        # Only adds types that the user has in their records
        for type in type_info:
            if type.id in user_types_ids:
                new_type_info.append(type)
        type_info = new_type_info

    return type_info


# Gets users personal health info
def get_user_health_entries():
    # Gets all users health info
    user_health_entries = db.session.query(UserHealth).join(Health).filter(
        UserHealth.user_id == current_user.id
    ).all()

    return user_health_entries

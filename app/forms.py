from flask_wtf import FlaskForm
from wtforms import (DateField, StringField, PasswordField, SubmitField,
                     TextAreaField, SelectField, TimeField)
from wtforms.validators import (InputRequired, Length, ValidationError,
                                EqualTo, Email, DataRequired, Optional)
from wtforms.fields import DateTimeLocalField
from config import (MIN_FIRST_NAME_LENGTH, MAX_FIRST_NAME_LENGTH,
                    MIN_LAST_NAME_LENGTH, MAX_LAST_NAME_LENGTH,
                    MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
                    MIN_HEALTH_LENGTH, MAX_HEALTH_LENGTH,
                    MIN_DESC_LENGTH, MAX_DESC_LENGTH,
                    MIN_EMAIL_LENGTH, MAX_EMAIL_LENGTH,
                    MIN_REMINDER_LENGTH, MAX_REMINDER_LENGTH)
from . models import User
from zoneinfo import ZoneInfo
from datetime import date, datetime


class RegisterForm(FlaskForm):
    first_name = StringField("First Name(s)", validators=[
        InputRequired(),
        Length(min=MIN_FIRST_NAME_LENGTH, max=MAX_FIRST_NAME_LENGTH)],
        render_kw={"placeholder": "First Name(s)"}
    )

    last_name = StringField("Surname(s)", validators=[
        InputRequired(),
        Length(min=MIN_LAST_NAME_LENGTH, max=MAX_LAST_NAME_LENGTH)],
        render_kw={"placeholder": "Surname(s)"}
    )

    date_of_birth = DateField(
        "Date of Birth",
        format="%Y-%m-%d",
        validators=[InputRequired()]
    )

    email = StringField("Email", validators=[
        DataRequired("Please enter an email"),
        Email(check_deliverability=True),
        Length(min=MIN_EMAIL_LENGTH, max=MAX_EMAIL_LENGTH)],
        render_kw={"placeholder": "Email"}
    )

    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH),
        EqualTo("confirm_password", "Passwords do not match!")],
        render_kw={"placeholder": "Password"}
    )

    confirm_password = PasswordField("Confirm Password", validators=[
        InputRequired(),
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH)],
        render_kw={"placeholder": "Confirm Password"}
    )

    submit = SubmitField("Register")

    # Ensures that the date of birth is not in the future or impossible
    def validate_date_of_birth(self, date_of_birth):
        if date_of_birth.data and date_of_birth.data > date.today():
            raise ValidationError(
                "Date of birth cannot be in the future"
            )

    # Checks if username already exists
    def validate_email(self, email):
        existing_user = User.query.filter_by(
            email=email.data).first()

        # Only raises error for verified users - others redirect to verify page
        if existing_user and existing_user.is_verified:
            raise ValidationError(
                "There is already an account for that email."
            )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        InputRequired("Please enter an email"),
        Email(check_deliverability=True),
        Length(min=MIN_EMAIL_LENGTH, max=MAX_EMAIL_LENGTH)],
        render_kw={"placeholder": "Email"})

    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH)],
        render_kw={"placeholder": "Password"}
    )

    submit = SubmitField("Login")


class ResetPasswordForm(FlaskForm):
    email = StringField("Email", validators=[
        Email(check_deliverability=True),
        Length(min=MIN_EMAIL_LENGTH, max=MAX_EMAIL_LENGTH),
        Optional()],
        render_kw={"placeholder": "Email"})

    password = PasswordField("Password", validators=[
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH),
        EqualTo("confirm_password", "Passwords do not match!"),
        Optional()],
        render_kw={"placeholder": "Password"}
    )

    confirm_password = PasswordField("Confirm Password", validators=[
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH),
        Optional()],
        render_kw={"placeholder": "Confirm Password"}
    )

    submit = SubmitField("Reset Password")

    # Ensures email exists
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if not existing_user_email:
            raise ValidationError(
                "There is no account for this email"
            )


class AddHealthInfoForm(FlaskForm):
    name = StringField("Name", validators=[
        InputRequired(),
        Length(min=MIN_HEALTH_LENGTH, max=MAX_HEALTH_LENGTH)],
        render_kw={"placeholder": "Name"}
    )

    default_desc = TextAreaField("Default Description", validators=[
        InputRequired(),
        Length(min=MIN_DESC_LENGTH, max=MAX_DESC_LENGTH)],
        render_kw={"placeholder": "Default Description"}
    )

    type_id = SelectField("Type", choices=[], coerce=int,
                          validators=[InputRequired()])

    submit = SubmitField("Add Info")

    # Ensures type id is not negative or invalid
    def validate_type_id(self, type_id):
        if type_id.data < 0:
            raise ValidationError(
                "Type ID is invalid"
            )


class AddReminderForm(FlaskForm):
    name = StringField("Name", validators=[
        InputRequired(),
        Length(min=MIN_REMINDER_LENGTH, max=MAX_REMINDER_LENGTH)],
        render_kw={"placeholder": "Name"}
    )

    desc = TextAreaField("Description", validators=[
        InputRequired(),
        Length(min=MIN_DESC_LENGTH, max=MAX_DESC_LENGTH),
        Optional()],
        render_kw={"placeholder": "Description"}
    )

    type_id = SelectField("Type", choices=[], coerce=int,
                          validators=[InputRequired()])

    appointment_datetime = DateTimeLocalField(
        "Appointment Date & Time",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()]
    )

    medication_time = TimeField(
        "Medication Time",
        format="%H:%M",
        validators=[Optional()]
    )

    submit = SubmitField("Add Reminder")

    # Ensures type id is not negative or invalid
    def validate_type_id(self, type_id):
        if type_id.data < 0:
            raise ValidationError(
                "Type ID is invalid"
            )

    # Ensures that the appointment datetime is not in the past
    def validate_appointment_datetime(self, appointment_datetime):
        if appointment_datetime.data:
            nz_tz = ZoneInfo("Pacific/Auckland")
            scheduled_time = appointment_datetime.data.replace(tzinfo=nz_tz)
            if scheduled_time < datetime.now(nz_tz):
                raise ValidationError(
                    "Date has already passed"
                )

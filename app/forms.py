from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     TextAreaField, SelectField)
from wtforms.validators import (InputRequired, Length, ValidationError,
                                EqualTo, Email, DataRequired, Optional)
from config import (MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH,
                    MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
                    MIN_HEALTH_LENGTH, MAX_HEALTH_LENGTH,
                    MIN_DESC_LENGTH, MAX_DESC_LENGTH)
from . models import User


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        InputRequired(),
        Length(min=MIN_USERNAME_LENGTH, max=MAX_USERNAME_LENGTH)],
        render_kw={"placeholder": "Username"}
    )

    email = StringField("Email", validators=[
        DataRequired("Please enter an email"),
        Email(check_deliverability=True)],
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

    # Checks if username already exists
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                "There is already an account for that email."
            )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        InputRequired("Please eneter an email"),
        Email(check_deliverability=True)],
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
                          validators=[DataRequired()])

    submit = SubmitField("Reset Password")

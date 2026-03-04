from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField)
from wtforms.validators import (InputRequired, Length,
                                EqualTo, Email, DataRequired)
from config import (MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH,
                    MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        InputRequired(),
        Length(min=MIN_USERNAME_LENGTH, max=MAX_USERNAME_LENGTH)],
        render_kw={"placeholder": "Username"}
    )

    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])

    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH),
        EqualTo("confirm_password", "Passwords do not match!")],
        render_kw={"placeholder": "Password"}
    )

    confirm_password = PasswordField("Confirm_Password", validators=[
        InputRequired(),
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH)],
        render_kw={"placeholder": "Confirm Password"}
    )

    submit = SubmitField("Register")

    # Checks if username already exists
    """def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one."
            )"""


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        InputRequired(),
        Email()
    ])

    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH)],
        render_kw={"placeholder": "Password"}
    )

    submit = SubmitField("Login")

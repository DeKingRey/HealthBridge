from flask_wtf import wtforms, FlaskForm
from wtforms import (StringField, PasswordField, SubmitField)
from wtforms.validators import (InputRequired, Length, ValidationError,
                                EqualTo)
from config import (MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH,
                    MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
                    DB)
from models import User



class RegisterForm(FlaskForm):
    username = StringField(validators=[
        InputRequired(),
        Length(min=MIN_USERNAME_LENGTH, max=MAX_USERNAME_LENGTH)],
        render_kw={"placeholder", "Username"}
    )

    password = PasswordField(validators=[
        InputRequired(),
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH),
        EqualTo("confirm_password", "Passwords do not match!")],
        render_kw={"placeholder", "Password"}
    )

    confirm_password = PasswordField(validators=[
        InputRequired(),
        Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH)],
        render_kw={"placeholder", "Confirm Password"}
    )

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(name=)

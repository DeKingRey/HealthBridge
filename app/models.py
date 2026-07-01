from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32), nullable=False, unique=False)
    last_name = db.Column(db.String(42), nullable=False, unique=False)
    date_of_birth = db.Column(db.Date, nullable=False)

    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    user_links = db.relationship("UserHealth", back_populates="user")
    reminder = db.relationship("Reminder", backref="user", lazy=True)


class HealthType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    health = db.relationship("Health", backref="type", lazy=True)


class Health(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    default_description = db.Column(db.String(500))

    type_id = db.Column(db.Integer,
                        db.ForeignKey("health_type.id"))

    is_public = db.Column(db.Boolean, default=False)

    health_links = db.relationship("UserHealth", back_populates="health")


class UserHealth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("user.id"), nullable=False)
    health_id = db.Column(db.Integer,
                          db.ForeignKey("health.id"), nullable=False)
    description = db.Column(db.String(500))

    user = db.relationship("User", back_populates="user_links")
    health = db.relationship("Health", back_populates="health_links")


class ReminderType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    reminder = db.relationship("Reminder", backref="type", lazy=True)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("user.id"), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))

    type_id = db.Column(db.Integer, db.ForeignKey("reminder_type.id"))

    scheduled_time = db.Column(db.DateTime, nullable=False)

    status_id = db.Column(db.Integer, db.ForeignKey("status.id"))
    status = db.relationship("Status", backref="reminders")


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

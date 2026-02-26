from config import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    user_links = db.relationship("UserHealth", back_populates="user")


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    health = db.relationship("Health", backref="type", lazy=True)


class Health(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    default_description = db.Column(db.String(500))

    type_id = db.Column(db.Integer,
                        db.ForeignKey("type.id"))
    health_links = db.relationship("UserHealth", back_populates="health")


class UserHealth(db.Model):
    user_id = db.Column(db.Integer,
                        db.ForeignKey("user.id"), primary_key=True)
    health_id = db.Column(db.Integer,
                          db.ForeignKey("health.id"), primary_key=True)
    description = db.Column(db.String(500))

    user = db.relationship("User", back_populates="user_links")
    health = db.relationship("Health", back_populates="health_links")

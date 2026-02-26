"""Docstring Health Bridge
A health tracker, specifically designed for the elderly.
Users can easily add their personal health info for doctors to easily find and read
Users can also set reminders for medicine or appointments
The app is very simple to use and targeted towards mobile users (as elderly tend to use mobile)
By Miguel Monreal on 27/02/2026"""

from flask import Flask
from config 
import os

# Initialises app
app = Flask(__name__)

# Initialize the DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "recipes.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.config["SECRET_KEY"] = "secret_shhhh"


@app.route("/")
def home():
    return "hi"


if __name__ == "__main__":
    app.run(debug=True)

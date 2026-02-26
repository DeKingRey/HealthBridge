"""Docstring Health Bridge
A health tracker, specifically designed for the elderly.
Users can easily add their personal health info for doctors to easily find and read
Users can also set reminders for medicine or appointments
The app is very simple to use and targeted towards mobile users (as elderly tend to use mobile)
By Miguel Monreal on 27/02/2026"""

from flask import Flask

# Initialises app
app = Flask(__name__)


@app.route("/")
def home():
    return "hi"


if __name__ == "__main__":
    app.run(debug=True)

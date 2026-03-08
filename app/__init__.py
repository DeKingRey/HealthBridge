from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_mail import Mail
import os

# Sets up extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
load_dotenv()


def create_app():
    """Sets up the application"""
    app = Flask(__name__)

    # Sets up config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Sets up mail config
    app.config['MAIL_SERVER'] = 'live.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'api'
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    # Initializes extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Redirects user to login page if they go to login_required page
    login_manager.login_view = "main.login"

    # Registers the routes blueprint
    from . routes import main
    app.register_blueprint(main)

    return app

"""
Application factory and core extensions for the trading journal Flask app.

This module defines a `create_app` function that sets up the Flask application,
configures extensions, registers blueprints, and creates database tables. It
reads configuration from environment variables using python-dotenv to support
easy deployment across environments.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# Instantiate the database extension outside of create_app so models can import
# it without causing circular imports.
db = SQLAlchemy()

# Set up Flask-Login. The login_view specifies the endpoint name that
# unauthenticated users will be redirected to.
login_manager = LoginManager()
login_manager.login_view = 'main.login'


def create_app() -> Flask:
    """Application factory to create and configure the Flask app instance."""
    # Load environment variables from a .env file if present. This allows
    # developers to set SECRET_KEY and DATABASE_URL locally without exposing
    # them in version control.
    load_dotenv()

    app = Flask(__name__)

    # Pull secret key and database URI from environment variables, providing
    # sensible fallbacks for development. In production you should set these
    # explicitly.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///journal.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the app instance.
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register the main blueprint containing routes and views.
    from .routes import bp as main_bp  # type: ignore
    app.register_blueprint(main_bp)

    # Create database tables at app startup. In larger applications you'd use
    # migrations (Flask-Migrate/Alembic), but for a simple journal we can
    # automatically create the schema on launch.
    with app.app_context():
        db.create_all()

    return app

from flask import Flask
from flask_cors import CORS

from api2.globals import (
    SESSION_SECRET,
    SESSION_SAME_SITE,
    SESSION_HTTPS_ONLY,
    build_allowed_origins,
)
from api2.extensions import init_oauth
from api2.services.data_store import ensure_data_file
from api2.routes.core import core_bp
from api2.routes.auth import auth_bp
from api2.routes.guilds import guilds_bp
from api2.routes.bot import bot_bp


def create_app() -> Flask:
    """Application factory for the Flask-based API 2.0 backend."""
    app = Flask(__name__)

    # Session cookie and secret settings are centralized in globals.py.
    app.config["SECRET_KEY"] = SESSION_SECRET
    app.config["SESSION_COOKIE_SAMESITE"] = SESSION_SAME_SITE
    app.config["SESSION_COOKIE_SECURE"] = SESSION_HTTPS_ONLY

    # Allow browser clients (frontend) to include session cookies.
    CORS(app, origins=build_allowed_origins(), supports_credentials=True)

    # Register OAuth client and ensure persistent storage exists.
    init_oauth(app)
    ensure_data_file()

    # Register route groups (blueprints) to keep modules focused.
    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(guilds_bp)
    app.register_blueprint(bot_bp)

    return app

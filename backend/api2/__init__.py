from flask import Flask
from flask_cors import CORS
from flask import g, request
from time import perf_counter

from api2.globals import (
    SESSION_SECRET,
    SESSION_SAME_SITE,
    SESSION_HTTPS_ONLY,
    build_allowed_origins,
)
from api2.debug import debug_kv, get_logger
from api2.extensions import init_oauth
from api2.services.data_store import ensure_data_file
from api2.routes.core import core_bp
from api2.routes.auth import auth_bp
from api2.routes.guilds import guilds_bp
from api2.routes.bot import bot_bp


logger = get_logger("app")


def create_app() -> Flask:
    """Application factory for the Flask-based API 2.0 backend."""
    app = Flask(__name__)
    logger.info("Creating Flask application")

    # Session cookie and secret settings are centralized in globals.py.
    app.config["SECRET_KEY"] = SESSION_SECRET
    app.config["SESSION_COOKIE_SAMESITE"] = SESSION_SAME_SITE
    app.config["SESSION_COOKIE_SECURE"] = SESSION_HTTPS_ONLY
    debug_kv(
        logger,
        "Session cookie configuration",
        same_site=SESSION_SAME_SITE,
        secure=SESSION_HTTPS_ONLY,
    )

    # Allow browser clients (frontend) to include session cookies.
    allowed_origins = build_allowed_origins()
    CORS(app, origins=allowed_origins, supports_credentials=True)
    debug_kv(logger, "CORS origins configured", origins=allowed_origins)

    @app.before_request
    def _log_request_start() -> None:
        g._request_started_at = perf_counter()
        debug_kv(
            logger,
            "Request start",
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            origin=request.headers.get("Origin"),
        )

    @app.after_request
    def _log_request_end(response):
        started = getattr(g, "_request_started_at", None)
        duration_ms = None
        if isinstance(started, float):
            duration_ms = round((perf_counter() - started) * 1000, 2)

        debug_kv(
            logger,
            "Request end",
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response

    # Register OAuth client and ensure persistent storage exists.
    init_oauth(app)
    ensure_data_file()

    # Register route groups (blueprints) to keep modules focused.
    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(guilds_bp)
    app.register_blueprint(bot_bp)

    logger.info("Application startup complete")

    return app

from flask import Blueprint, jsonify

from api2.debug import debug_kv, get_logger


core_bp = Blueprint("core", __name__)
logger = get_logger("routes.core")


@core_bp.get("/")
def home():
    """Simple root endpoint to verify the API is online."""
    debug_kv(logger, "Root endpoint called")
    return jsonify({"message": "AutoMod API 2.0 (Flask)"})


@core_bp.route("/healthz", methods=["GET", "HEAD"])
def healthz():
    """Health check endpoint for uptime monitors."""
    debug_kv(logger, "Health check endpoint called")
    return jsonify({"status": "ok"})

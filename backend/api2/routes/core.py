from flask import Blueprint, jsonify


core_bp = Blueprint("core", __name__)


@core_bp.get("/")
def home():
    """Simple root endpoint to verify the API is online."""
    return jsonify({"message": "AutoMod API 2.0 (Flask)"})


@core_bp.route("/healthz", methods=["GET", "HEAD"])
def healthz():
    """Health check endpoint for uptime monitors."""
    return jsonify({"status": "ok"})

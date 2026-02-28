from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from api2.services.data_store import load_bot_metrics, load_data, save_data
from api2.services.validators import validate_bot_token
from api2.state import BOT_METRICS, BOT_PROCESS


bot_bp = Blueprint("bot", __name__)


@bot_bp.get("/api/bot/status")
def bot_status():
    """Report whether optional bot sidecar mode is enabled/running."""
    run_bot = os.getenv("RUN_BOT_WITH_BACKEND", "false").lower() == "true"

    if not run_bot:
        return jsonify({
            "enabled": False,
            "running": False,
            "detail": "RUN_BOT_WITH_BACKEND is false",
        })

    if BOT_PROCESS is None:
        return jsonify({
            "enabled": True,
            "running": False,
            "detail": "Bot process has not been started",
        })

    exit_code = BOT_PROCESS.poll()
    if exit_code is None:
        return jsonify({"enabled": True, "running": True, "pid": BOT_PROCESS.pid})

    return jsonify({
        "enabled": True,
        "running": False,
        "pid": BOT_PROCESS.pid,
        "exit_code": exit_code,
        "detail": "Bot process exited",
    })


@bot_bp.get("/api/public/stats")
def public_stats():
    """Return non-sensitive bot/guild stats for the public landing page."""
    data = load_data()
    stored_guild_count, stored_updated_at = load_bot_metrics(data)

    reported_guild_count = BOT_METRICS.get("guild_count")
    reported_updated_at = BOT_METRICS.get("updated_at")

    if not isinstance(reported_guild_count, int):
        reported_guild_count = stored_guild_count

    if not isinstance(reported_updated_at, str):
        reported_updated_at = stored_updated_at

    if isinstance(reported_guild_count, int):
        guild_count = reported_guild_count
        source = "bot"
    else:
        guild_count = len(data.get("guilds", {}))
        source = "stored"

    return jsonify(
        {
            "protected_guilds": guild_count,
            "source": source,
            "updated_at": reported_updated_at,
        }
    )


@bot_bp.post("/api/internal/bot/metrics")
def update_bot_metrics():
    """Receive trusted metric updates from the bot process."""
    if not validate_bot_token(request):
        return jsonify({"detail": "invalid bot token"}), 401

    payload = request.get_json(silent=True) or {}
    guild_count = payload.get("guild_count")
    if not isinstance(guild_count, int) or guild_count < 0:
        return jsonify({"detail": "guild_count must be an integer >= 0"}), 400

    updated_at = datetime.now(timezone.utc).isoformat()
    BOT_METRICS["guild_count"] = guild_count
    BOT_METRICS["updated_at"] = updated_at

    data = load_data()
    data["bot_metrics"] = {"guild_count": guild_count, "updated_at": updated_at}
    save_data(data)

    return jsonify({"ok": True, "guild_count": guild_count, "updated_at": updated_at})


@bot_bp.get("/api/internal/bot/metrics")
def get_bot_metrics():
    """Return in-memory and persisted metric snapshots for debugging."""
    if not validate_bot_token(request):
        return jsonify({"detail": "invalid bot token"}), 401

    data = load_data()
    stored_guild_count, stored_updated_at = load_bot_metrics(data)

    return jsonify(
        {
            "memory": {
                "guild_count": BOT_METRICS.get("guild_count"),
                "updated_at": BOT_METRICS.get("updated_at"),
            },
            "stored": {"guild_count": stored_guild_count, "updated_at": stored_updated_at},
        }
    )

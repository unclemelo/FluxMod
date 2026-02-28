from __future__ import annotations

import uuid

from flask import Blueprint, jsonify, request

from api2.services.auth_helpers import require_user
from api2.services.data_store import load_data, save_data
from api2.services.validators import ValidationError, parse_rule_payload


guilds_bp = Blueprint("guilds", __name__)


@guilds_bp.get("/api/guilds")
@require_user
def list_guilds():
    """List known guilds with a computed rule count per guild."""
    data = load_data()
    guilds = []

    for guild_id, info in data.get("guilds", {}).items():
        rule_count = sum(1 for rule in data.get("rules", []) if rule.get("guild_id") == guild_id)
        guilds.append({"id": guild_id, "name": info.get("name"), "rule_count": rule_count})

    return jsonify(guilds)


@guilds_bp.get("/api/guilds/<guild_id>/rules")
@require_user
def list_rules(guild_id: str):
    """Return all rules for one guild."""
    data = load_data()
    rules = [rule for rule in data.get("rules", []) if rule.get("guild_id") == guild_id]
    return jsonify(rules)


@guilds_bp.post("/api/guilds/<guild_id>/rules")
@require_user
def create_rule(guild_id: str):
    """Create a new rule inside the selected guild."""
    payload = request.get_json(silent=True) or {}

    try:
        normalized = parse_rule_payload(payload)
    except ValidationError as exc:
        return jsonify({"detail": str(exc)}), 400

    data = load_data()
    guilds = data.setdefault("guilds", {})
    guilds.setdefault(guild_id, {"name": None})

    rule = {"id": str(uuid.uuid4()), "guild_id": guild_id, **normalized}
    data.setdefault("rules", []).append(rule)
    save_data(data)

    return jsonify(rule), 201


@guilds_bp.put("/api/rules/<rule_id>")
@require_user
def update_rule(rule_id: str):
    """Update an existing rule by id."""
    payload = request.get_json(silent=True) or {}

    try:
        normalized = parse_rule_payload(payload)
    except ValidationError as exc:
        return jsonify({"detail": str(exc)}), 400

    data = load_data()
    rules = data.get("rules", [])

    for index, rule in enumerate(rules):
        if rule.get("id") == rule_id:
            updated_rule = {**rule, **normalized}
            rules[index] = updated_rule
            save_data(data)
            return jsonify(updated_rule)

    return jsonify({"detail": "rule not found"}), 404


@guilds_bp.delete("/api/rules/<rule_id>")
@require_user
def delete_rule(rule_id: str):
    """Delete a rule by id."""
    data = load_data()
    rules = data.get("rules", [])

    for index, rule in enumerate(rules):
        if rule.get("id") == rule_id:
            rules.pop(index)
            save_data(data)
            return "", 204

    return jsonify({"detail": "rule not found"}), 404

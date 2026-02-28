from __future__ import annotations

import os
from flask import Request


class ValidationError(ValueError):
    """Raised when request data fails backend validation."""


REQUIRED_RULE_FIELDS = {"name", "pattern", "action"}


def validate_bot_token(request: Request) -> bool:
    """Check optional bot token authentication for internal endpoints."""
    expected_token = os.getenv("BOT_API_TOKEN")
    provided_token = request.headers.get("x-bot-token")

    if expected_token and provided_token != expected_token:
        return False

    return True


def parse_rule_payload(payload: dict) -> dict:
    """Validate and normalize a rule payload from JSON body."""
    missing_fields = [field for field in REQUIRED_RULE_FIELDS if field not in payload]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    threshold = payload.get("threshold", 1)
    if not isinstance(threshold, int) or threshold < 1:
        raise ValidationError("threshold must be an integer >= 1")

    enabled = payload.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValidationError("enabled must be a boolean")

    return {
        "name": str(payload["name"]),
        "pattern": str(payload["pattern"]),
        "action": str(payload["action"]),
        "threshold": threshold,
        "enabled": enabled,
    }

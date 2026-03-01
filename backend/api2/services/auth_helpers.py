from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from flask import jsonify, session

from api2.debug import debug_kv, get_logger


logger = get_logger("services.auth")


def require_user(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that ensures a logged-in user exists in session."""

    @wraps(handler)
    def wrapper(*args: Any, **kwargs: Any):
        user = session.get("user")
        if not user:
            debug_kv(logger, "Authentication required but no session user found")
            return jsonify({"detail": "authentication required"}), 401
        debug_kv(
            logger,
            "Authenticated request",
            user_id=user.get("id") if isinstance(user, dict) else None,
        )
        return handler(*args, **kwargs)

    return wrapper

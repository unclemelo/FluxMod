from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from flask import jsonify, session


def require_user(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that ensures a logged-in user exists in session."""

    @wraps(handler)
    def wrapper(*args: Any, **kwargs: Any):
        user = session.get("user")
        if not user:
            return jsonify({"detail": "authentication required"}), 401
        return handler(*args, **kwargs)

    return wrapper

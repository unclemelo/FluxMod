from __future__ import annotations

import os

import httpx
from flask import Blueprint, jsonify, redirect, request, session

from api2.debug import debug_kv, get_logger
from api2.extensions import oauth
from api2.services.auth_helpers import require_user
from api2.globals import FRONTEND_URL, FLUXER_SCOPE, OAUTH_PROVIDER, OAUTH_REDIRECT_URI


auth_bp = Blueprint("auth", __name__)
logger = get_logger("routes.auth")


@auth_bp.get("/login")
def login():
    """Start OAuth login by redirecting the user to the provider."""
    debug_kv(logger, "Login endpoint invoked", provider=OAUTH_PROVIDER)
    client = oauth.create_client(OAUTH_PROVIDER)
    if client is None:
        logger.error("OAuth client is not configured", extra={"provider": OAUTH_PROVIDER})
        return jsonify({"detail": f"OAuth provider '{OAUTH_PROVIDER}' is not configured"}), 500

    return client.authorize_redirect(OAUTH_REDIRECT_URI, scope=FLUXER_SCOPE)


@auth_bp.get("/auth")
def auth_callback():
    """Handle OAuth callback, fetch profile, and save user in session."""
    debug_kv(logger, "OAuth callback received", provider=OAUTH_PROVIDER)
    client = oauth.create_client(OAUTH_PROVIDER)
    if client is None:
        logger.error("OAuth client is not configured", extra={"provider": OAUTH_PROVIDER})
        return jsonify({"detail": f"OAuth provider '{OAUTH_PROVIDER}' is not configured"}), 500

    try:
        token = client.authorize_access_token()
    except Exception:
        logger.warning("Primary token exchange failed; trying manual token exchange")
        # Fallback: manually exchange authorization code for token.
        code = request.args.get("code")
        if not code:
            logger.warning("OAuth callback missing authorization code")
            return jsonify({"detail": "Missing authorization code"}), 400

        with httpx.Client() as http_client:
            token_response = http_client.post(
                os.getenv("FLUXER_TOKEN_URL"),
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": OAUTH_REDIRECT_URI,
                    "client_id": os.getenv("FLUXER_CLIENT_ID"),
                    "client_secret": os.getenv("FLUXER_CLIENT_SECRET"),
                },
            )
            if token_response.status_code != 200:
                logger.error("Manual token exchange failed", extra={"status": token_response.status_code})
                return jsonify({"detail": f"Token exchange failed: {token_response.text}"}), 500
            token = token_response.json()

    if OAUTH_PROVIDER == "fluxer":
        user_endpoint = os.getenv("FLUXER_USER_ENDPOINT")
        if not user_endpoint:
            logger.error("FLUXER_USER_ENDPOINT missing in environment")
            return jsonify({"detail": "FLUXER_USER_ENDPOINT not configured"}), 500

        resp = client.get(user_endpoint, token=token)
        profile = resp.json()
        session["user"] = {
            "id": profile.get("sub") or profile.get("id"),
            "username": profile.get("name") or profile.get("preferred_username"),
        }
    else:
        resp = client.get("/users/@me", token=token)
        profile = resp.json()
        session["user"] = {
            "id": profile.get("id"),
            "username": profile.get("username"),
            "discriminator": profile.get("discriminator"),
        }

    debug_kv(
        logger,
        "OAuth session established",
        user_id=session.get("user", {}).get("id"),
        username=session.get("user", {}).get("username"),
        frontend_url=FRONTEND_URL,
    )

    return redirect(FRONTEND_URL, code=302)


@auth_bp.get("/logout")
def logout():
    """Clear user session and log out."""
    debug_kv(logger, "Logout endpoint invoked", had_user=bool(session.get("user")))
    session.pop("user", None)
    return jsonify({"detail": "logged out"})


@auth_bp.get("/api/me")
@require_user
def get_me():
    """Return the current authenticated user stored in session."""
    user = session.get("user")
    debug_kv(
        logger,
        "Session user fetched",
        user_id=user.get("id") if isinstance(user, dict) else None,
    )
    return jsonify(user)

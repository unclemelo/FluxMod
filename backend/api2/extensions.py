from flask import Flask
from authlib.integrations.flask_client import OAuth

from api2.debug import debug_kv, get_logger
from api2.globals import OAUTH_PROVIDER, FLUXER_SCOPE
import os


# Single OAuth registry used by the whole app.
oauth = OAuth()
logger = get_logger("extensions.oauth")


def init_oauth(app: Flask) -> None:
    """Initialize provider clients for OAuth login flows."""
    oauth.init_app(app)
    debug_kv(logger, "OAuth registry initialized", provider=OAUTH_PROVIDER)

    if OAUTH_PROVIDER == "fluxer":
        # Fluxer configuration comes directly from environment variables.
        oauth.register(
            name="fluxer",
            client_id=os.getenv("FLUXER_CLIENT_ID"),
            client_secret=os.getenv("FLUXER_CLIENT_SECRET"),
            access_token_url=os.getenv("FLUXER_TOKEN_URL"),
            authorize_url=os.getenv("FLUXER_AUTHORIZE_URL"),
            api_base_url=os.getenv("FLUXER_API_BASE_URL"),
            client_kwargs={"scope": FLUXER_SCOPE},
        )
        logger.info("Registered Fluxer OAuth client")

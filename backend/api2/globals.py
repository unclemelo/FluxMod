import os
import pathlib
from typing import Literal
from dotenv import load_dotenv

from api2.debug import debug_kv, get_logger


ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data.json"

# Load .env from the backend directory
load_dotenv(dotenv_path=str(ROOT / ".env"))


# OAuth / session configuration
SESSION_SECRET = os.getenv("SESSION_SECRET") or "melobytesarebestbytes"
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI") or "http://127.0.0.1:8000/auth"
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"
SESSION_SAME_SITE: Literal["lax", "strict", "none"] = os.getenv("SESSION_SAME_SITE", "none" if IS_PRODUCTION else "lax").lower() # type: ignore
SESSION_HTTPS_ONLY = os.getenv("SESSION_HTTPS_ONLY", str(IS_PRODUCTION)).lower() == "true"
FRONTEND_URL = os.getenv("FRONTEND_URL") or "http://localhost:3000"
OAUTH_PROVIDER = os.getenv("OAUTH_PROVIDER", "fluxer").lower()
FLUXER_SCOPE = os.getenv("FLUXER_SCOPE", "identify guilds")
logger = get_logger("globals")

def build_allowed_origins() -> list[str]:
    defaults = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://fluxmod-frontend.onrender.com"
    }

    if FRONTEND_URL:
        defaults.add(FRONTEND_URL)

    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    parsed_env_origins = {
        origin.strip()
        for origin in env_origins.split(",")
        if origin.strip()
    }

    origins = sorted(defaults | parsed_env_origins)
    debug_kv(
        logger,
        "Allowed origins resolved",
        frontend_url=FRONTEND_URL,
        count=len(origins),
    )
    return origins
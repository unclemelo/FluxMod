import json
from typing import Any

from api2.globals import DATA_FILE


def default_data() -> dict[str, Any]:
    """Return the baseline shape used by data.json."""
    return {"guilds": {}, "rules": []}


def ensure_data_file() -> None:
    """Create data.json if it does not exist yet."""
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        save_data(default_data())


def load_data() -> dict[str, Any]:
    """Load persisted backend data from disk."""
    if not DATA_FILE.exists():
        return default_data()

    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_data(data: dict[str, Any]) -> None:
    """Persist backend data to disk in a readable format."""
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_bot_metrics(data: dict[str, Any]) -> tuple[int | None, str | None]:
    """Extract bot metrics safely from persisted JSON payloads."""
    stored_metrics = data.get("bot_metrics")
    if not isinstance(stored_metrics, dict):
        return None, None

    stored_guild_count = stored_metrics.get("guild_count")
    stored_updated_at = stored_metrics.get("updated_at")

    guild_count = stored_guild_count if isinstance(stored_guild_count, int) else None
    updated_at = stored_updated_at if isinstance(stored_updated_at, str) else None
    return guild_count, updated_at

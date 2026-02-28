from __future__ import annotations

import subprocess
from typing import Any


# Runtime process reference for optional in-process bot mode.
BOT_PROCESS: subprocess.Popen[str] | None = None

# In-memory copy of public bot stats (also persisted to disk).
BOT_METRICS: dict[str, Any] = {
    "guild_count": None,
    "updated_at": None,
}

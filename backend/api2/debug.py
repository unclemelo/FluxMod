from __future__ import annotations

import logging
import os
from typing import Any


def is_debug_enabled() -> bool:
    value = (os.getenv("BACKEND_DEBUG") or os.getenv("DEBUG") or "false").strip().lower()
    return value in {"1", "true", "yes", "on"}


def configure_logging() -> None:
    level = logging.DEBUG if is_debug_enabled() else logging.INFO

    root_logger = logging.getLogger("fluxmod")
    root_logger.setLevel(level)

    if root_logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    )
    root_logger.addHandler(handler)


def get_logger(scope: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(f"fluxmod.{scope}")


def debug_kv(logger: logging.Logger, message: str, **kwargs: Any) -> None:
    if not logger.isEnabledFor(logging.DEBUG):
        return

    logger.debug("%s | %s", message, kwargs)

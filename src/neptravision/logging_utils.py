"""One place to configure logging, backed by Rich for readable console output.

Library code calls ``get_logger(__name__)`` and never configures handlers itself;
the CLI calls ``setup_logging()`` once at startup. This keeps log configuration out
of importable modules (so importing the package never spams a host application).
"""

from __future__ import annotations

import logging
import os

from rich.logging import RichHandler

_CONFIGURED = False


def setup_logging(level: str | None = None) -> None:
    """Configure root logging once. Idempotent.

    Level resolution order: explicit ``level`` arg → ``NEPTRAVISION_LOG_LEVEL`` env
    → ``INFO``.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    resolved = (level or os.environ.get("NEPTRAVISION_LOG_LEVEL") or "INFO").upper()
    logging.basicConfig(
        level=resolved,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module logger, ensuring logging is configured at least minimally."""
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(name)

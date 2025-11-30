import logging
from typing import Optional


def configure_logging(level: int = logging.INFO) -> None:
    """Configure structured logging once per process."""
    if getattr(configure_logging, "_is_configured", False):
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler()],
        force=True,
    )
    configure_logging._is_configured = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name or "backend")


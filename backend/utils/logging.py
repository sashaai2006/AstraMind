"""Logging utilities."""
import logging
import sys
from typing import Optional

_logging_configured = False

def configure_logging(level: int = logging.INFO) -> None:
    """Configure logging for the application."""
    global _logging_configured
    if _logging_configured:
        return
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    _logging_configured = True

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    if not _logging_configured:
        configure_logging()
    return logging.getLogger(name)


"""
Logging configuration for the Web Research Agent.

Provides structured logging with consistent formatting across the application.
"""

import logging
import sys
from typing import Literal


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING",
    verbose: bool = False,
) -> logging.Logger:
    """
    Configure application logging.

    Args:
        level: The logging level to use.
        verbose: If True, sets level to DEBUG regardless of level parameter.

    Returns:
        The configured root logger.
    """
    if verbose:
        level = "DEBUG"

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    noisy_loggers = [
        "httpx",
        "httpcore",
        "openai",
        "primp",
        "rquest",
        "cookie_store",
        "urllib3",
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: The name for the logger (typically __name__).

    Returns:
        A configured logger instance.
    """
    return logging.getLogger(name)

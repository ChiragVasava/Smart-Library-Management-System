"""
logger.py

Centralized logging configuration for the Smart Library Management System.
Demonstrates: module-level singleton pattern, context managers, logging.
"""

import logging
from contextlib import contextmanager
from typing import Iterator

from constants import LOG_FILE_PATH

_logger: logging.Logger = logging.getLogger("smart_library")
_logger.setLevel(logging.INFO)

if not _logger.handlers:
    _stream_handler = logging.StreamHandler()
    _formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    _stream_handler.setFormatter(_formatter)
    _logger.addHandler(_stream_handler)


def get_logger() -> logging.Logger:
    """Return the shared library logger instance."""
    return _logger


@contextmanager
def log_transaction(transaction_name: str) -> Iterator[None]:
    """
    Context manager that logs the start and end of a transaction.

    Demonstrates: 'with' statement / context manager AST node.
    """
    logger = get_logger()
    logger.info("Starting transaction: %s", transaction_name)
    try:
        yield
    except Exception as exc:  # noqa: BLE001
        logger.error("Transaction '%s' failed: %s", transaction_name, exc)
        raise
    else:
        logger.info("Transaction '%s' completed successfully", transaction_name)


def write_log_entry(entry: str) -> None:
    """
    Append a raw log entry to the log file on disk.

    Demonstrates: file I/O with a context manager ('with open(...)').
    """
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(entry + "\n")

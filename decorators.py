"""
decorators.py

Custom decorators used across the Smart Library Management System.
Demonstrates: custom decorators, nested functions, functools.wraps.
"""

import functools
import time
from typing import Any, Callable, TypeVar

from exceptions import MembershipError
from logger import get_logger

F = TypeVar("F", bound=Callable[..., Any])

logger = get_logger()


def admin_required(func: F) -> F:
    """
    Decorator that ensures the calling member has admin privileges.

    Demonstrates: custom decorator, nested wrapper function, *args/**kwargs.
    """

    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            member = self.requesting_member
            is_admin = member.is_admin
        except AttributeError:
            member = None
            is_admin = False

        if member is None or not is_admin:
            raise MembershipError("Admin privileges are required for this action")
        return func(self, *args, **kwargs)

    return wrapper  # type: ignore[return-value]


def timed(func: F) -> F:
    """
    Decorator that logs the execution time of the wrapped function.

    Demonstrates: nested function, closures, decorator with side effects.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info("%s executed in %.6f seconds", func.__name__, elapsed)
        return result

    return wrapper  # type: ignore[return-value]


def retry(max_attempts: int = 3) -> Callable[[F], F]:
    """
    Decorator factory that retries a function call on failure.

    Demonstrates: decorator factory (decorator returning a decorator),
    nested functions, while loop, try/except.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            last_error: Exception | None = None
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
                    attempts += 1
                    logger.warning(
                        "Attempt %d/%d for %s failed: %s",
                        attempts,
                        max_attempts,
                        func.__name__,
                        exc,
                    )
            assert last_error is not None
            raise last_error

        return wrapper  # type: ignore[return-value]

    return decorator

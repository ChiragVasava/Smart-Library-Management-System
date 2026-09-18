"""
utils.py

General-purpose helper functions used across the library system.
Demonstrates: boundary conditions, default values, optional values,
list/dict comprehensions, lambda expressions.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from constants import FINE_PER_DAY


def calculate_fine(days_overdue: int, discount_rate: float = 0.0) -> float:
    """
    Calculate the fine owed for a number of overdue days.

    Boundary conditions:
        - days_overdue <= 0 returns 0.0
        - discount_rate is clamped between 0.0 and 1.0
    """
    if days_overdue <= 0:
        return 0.0
    clamped_discount = max(0.0, min(discount_rate, 1.0))
    raw_fine = days_overdue * FINE_PER_DAY
    return round(raw_fine * (1 - clamped_discount), 2)


def clamp(value: int, minimum: int, maximum: int) -> int:
    """Clamp an integer value to the inclusive [minimum, maximum] range."""
    if minimum > maximum:
        raise ValueError("minimum cannot be greater than maximum")
    return max(minimum, min(value, maximum))


def chunk_list(items: List[int], size: int) -> List[List[int]]:
    """
    Split a list into chunks of the given size.

    Demonstrates: list comprehension with slicing, boundary condition
    when size <= 0.
    """
    if size <= 0:
        return [items]
    return [items[i : i + size] for i in range(0, len(items), size)]


def group_by_first_letter(names: Iterable[str]) -> Dict[str, List[str]]:
    """
    Group a collection of names by their first letter (uppercased).

    Demonstrates: dictionary comprehension combined with a for loop.
    """
    groups: Dict[str, List[str]] = {}
    for name in names:
        if not name:
            continue
        key = name[0].upper()
        groups.setdefault(key, []).append(name)
    return groups


def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """
    Divide two numbers, returning None instead of raising on division by zero.

    Demonstrates: try/except, Optional return type, boundary condition.
    """
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return None


def is_valid_isbn(isbn: str) -> bool:
    """
    Return True if the given string is a plausible ISBN-13.

    Demonstrates: lambda usage, boundary condition on string length.
    """
    digits_only = "".join(filter(lambda ch: ch.isdigit(), isbn))
    return len(digits_only) == 13

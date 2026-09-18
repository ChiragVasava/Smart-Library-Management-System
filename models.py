"""
models.py

Core domain models for the Smart Library Management System.
Demonstrates: dataclasses, Enums, ABCs, inheritance, properties,
static methods, class methods, type hints, default values, optional values.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional

from constants import LOAN_PERIOD_DAYS, MAX_RENEWALS


class BookStatus(Enum):
    """Enumerates the possible states of a physical book."""

    AVAILABLE = auto()
    BORROWED = auto()
    RESERVED = auto()
    LOST = auto()


class MembershipType(Enum):
    """Enumerates the supported membership tiers."""

    STUDENT = "student"
    REGULAR = "regular"
    PREMIUM = "premium"


@dataclass
class Book:
    """Represents a single physical or digital book in the library."""

    title: str
    author: str
    isbn: str
    status: BookStatus = BookStatus.AVAILABLE
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tags: List[str] = field(default_factory=list)

    @property
    def available(self) -> bool:
        """Return True if the book can currently be borrowed."""
        return self.status == BookStatus.AVAILABLE

    def mark_borrowed(self) -> None:
        """Transition the book's status to BORROWED."""
        self.status = BookStatus.BORROWED

    def mark_returned(self) -> None:
        """Transition the book's status back to AVAILABLE."""
        self.status = BookStatus.AVAILABLE

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.title} by {self.author} ({self.id})"


@dataclass
class Loan:
    """Represents an active or historical loan of a Book to a Member."""

    book_id: str
    member_id: str
    borrowed_on: date = field(default_factory=date.today)
    due_date: Optional[date] = None
    returned_on: Optional[date] = None
    renewals: int = 0

    def __post_init__(self) -> None:
        if self.due_date is None:
            self.due_date = self.borrowed_on + timedelta(days=LOAN_PERIOD_DAYS)

    @property
    def is_overdue(self) -> bool:
        """Return True if the loan is unreturned and past its due date."""
        if self.returned_on is not None:
            return False
        return date.today() > self.due_date

    @property
    def days_overdue(self) -> int:
        """Return the number of days this loan is overdue (0 if not overdue)."""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

    def renew(self) -> bool:
        """
        Attempt to renew the loan.

        Returns True if the renewal succeeded, False if the renewal
        limit has already been reached.
        """
        if self.renewals >= MAX_RENEWALS:
            return False
        self.renewals += 1
        self.due_date = self.due_date + timedelta(days=LOAN_PERIOD_DAYS)
        return True


class Member(ABC):
    """
    Abstract base class representing a library member.

    Demonstrates: ABC, abstractmethod, inheritance, class methods,
    static methods, properties.
    """

    _registry_count: int = 0

    def __init__(self, name: str, email: str, is_admin: bool = False) -> None:
        Member._registry_count += 1
        self.member_id: str = f"M{Member._registry_count:04d}"
        self.name = name
        self.email = email
        self.is_admin = is_admin
        self.active = True
        self.borrowed_book_ids: List[str] = []

    @property
    def full_name(self) -> str:
        """Return the display-friendly full name of the member."""
        return self.name.strip().title()

    @property
    def is_active(self) -> bool:
        """Return whether the membership is currently active."""
        return self.active

    @abstractmethod
    def discount_rate(self) -> float:
        """Return the fine discount rate applicable to this member type."""
        raise NotImplementedError

    @abstractmethod
    def borrow_limit(self) -> int:
        """Return the maximum number of books this member may borrow."""
        raise NotImplementedError

    @staticmethod
    def validate_email(email: str) -> bool:
        """Return True if the given string looks like a valid email address."""
        return "@" in email and "." in email.split("@")[-1]

    @classmethod
    def total_members(cls) -> int:
        """Return the total number of members ever registered."""
        return cls._registry_count

    def deactivate(self) -> None:
        """Deactivate this member's account."""
        self.active = False

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<{self.__class__.__name__} {self.member_id} {self.full_name}>"


class Student(Member):
    """A student member, entitled to a discount on fines."""

    def __init__(self, name: str, email: str, university: str) -> None:
        super().__init__(name, email)
        self.university = university
        self.membership_type = MembershipType.STUDENT

    def discount_rate(self) -> float:
        return 0.5

    def borrow_limit(self) -> int:
        return 5


class RegularMember(Member):
    """A standard, non-discounted member."""

    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)
        self.membership_type = MembershipType.REGULAR

    def discount_rate(self) -> float:
        return 0.0

    def borrow_limit(self) -> int:
        return 3


class PremiumMember(Member):
    """A premium member with an increased borrow limit and no fines."""

    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)
        self.membership_type = MembershipType.PREMIUM

    def discount_rate(self) -> float:
        return 1.0

    def borrow_limit(self) -> int:
        return 10


def build_isbn_index(books: List[Book]) -> Dict[str, Book]:
    """
    Build a lookup dictionary keyed by ISBN.

    Demonstrates: dictionary comprehension.
    """
    return {book.isbn: book for book in books}


def sort_books_by_title(books: List[Book]) -> List[Book]:
    """
    Return books sorted alphabetically by title.

    Demonstrates: lambda expressions.
    """
    return sorted(books, key=lambda b: b.title.lower())


def available_books(books: List[Book]) -> List[Book]:
    """
    Return only the books that are currently available.

    Demonstrates: list comprehension.
    """
    return [b for b in books if b.available]

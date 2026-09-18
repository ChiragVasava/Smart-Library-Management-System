"""
membership.py

Manages library members: registration, validation, and borrowing rules.
Demonstrates: if/elif/else, custom exceptions, cross-file relationships,
type hints with Optional/List/Dict, nested functions.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from constants import MAX_BOOKS_PER_MEMBER
from exceptions import (
    BorrowLimitExceededError,
    MembershipExpiredError,
)
from logger import get_logger
from models import Member, PremiumMember, RegularMember, Student

logger = get_logger()


class MembershipService:
    """Manages the registry of members and enforces membership rules."""

    def __init__(self) -> None:
        self._members: Dict[str, Member] = {}

    def register_student(self, name: str, email: str, university: str) -> Student:
        """Register a new student member."""
        member = Student(name=name, email=email, university=university)
        self._members[member.member_id] = member
        logger.info("Registered student member: %s", member)
        return member

    def register_regular(self, name: str, email: str) -> RegularMember:
        """Register a new regular member."""
        member = RegularMember(name=name, email=email)
        self._members[member.member_id] = member
        logger.info("Registered regular member: %s", member)
        return member

    def register_premium(self, name: str, email: str) -> PremiumMember:
        """Register a new premium member."""
        member = PremiumMember(name=name, email=email)
        self._members[member.member_id] = member
        logger.info("Registered premium member: %s", member)
        return member

    def find_member(self, member_id: str) -> Optional[Member]:
        """Return the member with the given id, or None if not found."""
        return self._members.get(member_id)

    def classify_member(self, member: Member) -> str:
        """
        Return a human-readable classification for the member.

        Demonstrates: if / elif / else chain.
        """
        limit = member.borrow_limit()
        if limit >= 10:
            return "power-user"
        elif limit >= 5:
            return "frequent-borrower"
        elif limit >= 3:
            return "standard"
        else:
            return "limited"

    def validate_can_borrow(self, member: Member, additional: int = 1) -> None:
        """
        Validate that a member is allowed to borrow more books.

        Raises:
            MembershipExpiredError: if the member is not active.
            BorrowLimitExceededError: if borrowing would exceed the limit.
        """
        if not member.is_active:
            raise MembershipExpiredError(member.member_id)

        def _projected_total() -> int:
            """Nested helper computing the projected book count."""
            return len(member.borrowed_book_ids) + additional

        projected = _projected_total()
        effective_limit = min(member.borrow_limit(), MAX_BOOKS_PER_MEMBER)
        if projected > effective_limit:
            raise BorrowLimitExceededError(member.member_id, effective_limit)

    def active_members(self) -> List[Member]:
        """
        Return all currently active members.

        Demonstrates: list comprehension.
        """
        return [m for m in self._members.values() if m.is_active]

    def deactivate_member(self, member_id: str) -> bool:
        """Deactivate a member by id. Returns True if found and deactivated."""
        member = self._members.get(member_id)
        if member is None:
            return False
        member.deactivate()
        return True

"""
library_manager.py

The central orchestrator of the Smart Library Management System.
Ties together Inventory, MembershipService, PaymentProcessor, and
NotificationService to implement the core borrow/return business logic.

Demonstrates: cross-file relationships, business logic branching,
decorators, exception handling, logging, async integration.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from decorators import admin_required, timed
from exceptions import (
    BookNotAvailableError,
    BorrowLimitExceededError,
    LibraryError,
    MembershipExpiredError,
)
from inventory import Inventory
from logger import get_logger, log_transaction
from membership import MembershipService
from models import Book, Loan, Member
from notification import NotificationService
from payment import PaymentMethod, PaymentProcessor

logger = get_logger()


class LibraryManager:
    """
    Coordinates the full lifecycle of borrowing and returning books.

    This is the primary business-logic entry point used by main.py.
    """

    def __init__(
        self,
        inventory: Optional[Inventory] = None,
        membership_service: Optional[MembershipService] = None,
        payment_processor: Optional[PaymentProcessor] = None,
        notification_service: Optional[NotificationService] = None,
    ) -> None:
        self.inventory = inventory or Inventory()
        self.membership_service = membership_service or MembershipService()
        self.payment_processor = payment_processor or PaymentProcessor()
        self.notification_service = notification_service or NotificationService()
        self.active_loans: Dict[str, Loan] = {}
        self.requesting_member: Optional[Member] = None

    @timed
    def borrow_book(self, member: Member, book_id: str) -> Loan:
        """
        Execute the full borrow-book business workflow:

            Check Membership -> Check Inventory -> Create Loan -> Log

        Raises:
            MembershipExpiredError: if the member is inactive.
            BorrowLimitExceededError: if the member is at their limit.
            BookNotAvailableError: if the book cannot be checked out.
        """
        with log_transaction(f"borrow:{member.member_id}:{book_id}"):
            self.membership_service.validate_can_borrow(member)
            book = self.inventory.checkout(book_id)
            loan = Loan(book_id=book.id, member_id=member.member_id)
            self.active_loans[book.id] = loan
            member.borrowed_book_ids.append(book.id)
            logger.info("Loan created: %s", loan)
            return loan

    def return_book(
        self,
        member: Member,
        book_id: str,
        payment_method: Optional[PaymentMethod] = None,
    ) -> float:
        """
        Execute the full return-book business workflow:

            Check Inventory -> Calculate Fine -> Process Payment
            -> Send Notification -> Log Transaction

        Returns the fine amount that was charged (0.0 if none).
        """
        loan = self.active_loans.get(book_id)
        if loan is None:
            raise LibraryError(f"No active loan found for book '{book_id}'")

        fine = self._calculate_loan_fine(loan, member)
        days_overdue_snapshot = loan.days_overdue

        if fine > 0:
            if payment_method is None:
                raise LibraryError("Payment method required to settle outstanding fine")
            self.payment_processor.process_fine(payment_method, fine)

        self.inventory.check_in(book_id)
        self._finalize_return(loan, member, book_id)

        try:
            asyncio.run(
                self.notification_service.notify_overdue(
                    member.full_name, days_overdue_snapshot
                )
            )
        except RuntimeError:
            # Already inside an event loop (e.g. called from async context);
            # skip the notification in that edge case rather than crash.
            logger.warning("Could not send async notification synchronously")

        return fine

    def _calculate_loan_fine(self, loan: Loan, member: Member) -> float:
        """
        Compute the fine owed for a loan, applying the member's discount.

        Demonstrates: private helper method (business logic branch),
        if / else, property access across modules.
        """
        from utils import calculate_fine  # local import: keeps utils decoupled

        if not loan.is_overdue:
            return 0.0
        return calculate_fine(loan.days_overdue, member.discount_rate())

    def _finalize_return(self, loan: Loan, member: Member, book_id: str) -> None:
        """Update in-memory state once a book has been physically returned."""
        from datetime import date

        loan.returned_on = date.today()
        if book_id in member.borrowed_book_ids:
            member.borrowed_book_ids.remove(book_id)
        del self.active_loans[book_id]

    def renew_loan(self, book_id: str) -> bool:
        """
        Attempt to renew an active loan.

        Demonstrates: dictionary lookup, boolean business logic branch.
        """
        loan = self.active_loans.get(book_id)
        if loan is None:
            return False
        return loan.renew()

    def overdue_loans(self) -> List[Loan]:
        """
        Return all currently overdue loans.

        Demonstrates: list comprehension across a business collection.
        """
        return [loan for loan in self.active_loans.values() if loan.is_overdue]

    @admin_required
    def force_return_all(self, member: Member) -> int:
        """
        Administrative action: forcibly return every book a member holds,
        waiving all fines. Requires admin privileges.

        Demonstrates: custom decorator enforcement, for loop, side effects.
        """
        book_ids = list(member.borrowed_book_ids)
        count = 0
        for book_id in book_ids:
            if book_id in self.active_loans:
                self.inventory.check_in(book_id)
                self._finalize_return(self.active_loans[book_id], member, book_id)
                count += 1
        return count

    def add_book_to_catalog(self, book: Book) -> None:
        """Add a new book to the library's catalog."""
        self.inventory.add_book(book)

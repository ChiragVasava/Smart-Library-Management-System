"""
exceptions.py

Custom exception hierarchy for the Smart Library Management System.
Demonstrates: class inheritance, custom exceptions, docstrings.
"""


class LibraryError(Exception):
    """Base exception for all library-related errors."""

    def __init__(self, message: str = "A library error occurred") -> None:
        self.message = message
        super().__init__(self.message)


class MembershipError(LibraryError):
    """Raised when a membership-related rule is violated."""

    def __init__(self, message: str = "Membership error") -> None:
        super().__init__(message)


class MembershipExpiredError(MembershipError):
    """Raised when a member's subscription has expired."""

    def __init__(self, member_id: str) -> None:
        self.member_id = member_id
        super().__init__(f"Membership expired for member '{member_id}'")


class BookNotAvailableError(LibraryError):
    """Raised when a requested book is not available in inventory."""

    def __init__(self, book_id: str) -> None:
        self.book_id = book_id
        super().__init__(f"Book '{book_id}' is not available")


class BorrowLimitExceededError(LibraryError):
    """Raised when a member tries to borrow more than the allowed limit."""

    def __init__(self, member_id: str, limit: int) -> None:
        self.member_id = member_id
        self.limit = limit
        super().__init__(
            f"Member '{member_id}' has exceeded the borrow limit of {limit}"
        )


class PaymentError(LibraryError):
    """Base exception for payment-related failures."""

    def __init__(self, message: str = "Payment error") -> None:
        super().__init__(message)


class InsufficientFundsError(PaymentError):
    """Raised when a payment method has insufficient funds."""

    def __init__(self, amount: float) -> None:
        self.amount = amount
        super().__init__(f"Insufficient funds to process payment of {amount:.2f}")


class PaymentGatewayTimeoutError(PaymentError):
    """Raised when the external payment gateway times out."""

    def __init__(self, attempts: int) -> None:
        self.attempts = attempts
        super().__init__(f"Payment gateway timed out after {attempts} attempts")

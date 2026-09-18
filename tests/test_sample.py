"""
test_sample.py

A small hand-written sample test suite. This is NOT meant to be
exhaustive — it exists to (a) prove the project is importable and
runnable under pytest, and (b) give TestForge AI a reference point
for what "correct" generated tests should look like.
"""

import pytest

from exceptions import BookNotAvailableError, BorrowLimitExceededError
from inventory import Inventory
from library_manager import LibraryManager
from membership import MembershipService
from models import Book
from payment import CashPayment
from utils import calculate_fine, chunk_list, safe_divide


def test_book_defaults_to_available():
    book = Book(title="1984", author="George Orwell", isbn="1234567890123")
    assert book.available is True


def test_inventory_checkout_marks_unavailable():
    inventory = Inventory()
    book = Book(title="Dune", author="Frank Herbert", isbn="1111111111111")
    inventory.add_book(book)

    inventory.checkout(book.id)

    assert book.available is False


def test_inventory_checkout_raises_when_unavailable():
    inventory = Inventory()
    book = Book(title="Dune", author="Frank Herbert", isbn="1111111111111")
    inventory.add_book(book)
    inventory.checkout(book.id)

    with pytest.raises(BookNotAvailableError):
        inventory.checkout(book.id)


def test_borrow_limit_enforced():
    manager = LibraryManager()
    member = manager.membership_service.register_regular("Sam", "sam@example.com")

    for i in range(3):
        book = Book(title=f"Book {i}", author="Author", isbn=str(i) * 13)
        manager.inventory.add_book(book)
        manager.borrow_book(member, book.id)

    extra_book = Book(title="Extra", author="Author", isbn="9" * 13)
    manager.inventory.add_book(extra_book)

    with pytest.raises(BorrowLimitExceededError):
        manager.borrow_book(member, extra_book.id)


def test_borrow_and_return_full_flow():
    manager = LibraryManager()
    member = manager.membership_service.register_student(
        "Ada", "ada@example.com", "MSU Baroda"
    )
    book = Book(title="Clean Code", author="Robert C. Martin", isbn="9780132350884")
    manager.inventory.add_book(book)

    manager.borrow_book(member, book.id)
    fine = manager.return_book(member, book.id, payment_method=CashPayment(50.0))

    assert fine == 0.0
    assert book.available is True


@pytest.mark.parametrize(
    "days_overdue,discount,expected",
    [
        (0, 0.0, 0.0),
        (-3, 0.5, 0.0),
        (4, 0.0, 2.0),
        (4, 0.5, 1.0),
    ],
)
def test_calculate_fine_boundaries(days_overdue, discount, expected):
    assert calculate_fine(days_overdue, discount) == expected


def test_chunk_list_handles_non_divisible_length():
    assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_safe_divide_returns_none_on_zero():
    assert safe_divide(10, 0) is None
    assert safe_divide(10, 2) == 5.0


def test_membership_classification():
    service = MembershipService()
    premium = service.register_premium("Grace", "grace@example.com")
    assert service.classify_member(premium) == "power-user"

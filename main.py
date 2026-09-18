"""
main.py

Entry point that wires up the Smart Library Management System and
runs through a representative end-to-end scenario:

    Borrow Book -> Check Membership -> Check Inventory -> Calculate Fine
    -> Process Payment -> Send Notification -> Log Transaction

Run with:
    python main.py
"""

from __future__ import annotations

from constants import LIBRARY_NAME
from exceptions import LibraryError
from library_manager import LibraryManager
from logger import get_logger
from models import Book, available_books, build_isbn_index, sort_books_by_title
from payment import CashPayment

logger = get_logger()


def seed_catalog(manager: LibraryManager) -> None:
    """Populate the library with a handful of starter books."""
    starter_books = [
        Book(title="Clean Code", author="Robert C. Martin", isbn="9780132350884"),
        Book(title="The Pragmatic Programmer", author="Andrew Hunt", isbn="9780135957059"),
        Book(title="Design Patterns", author="Erich Gamma", isbn="9780201633610"),
    ]
    manager.inventory.bulk_add(starter_books)


def print_catalog_summary(manager: LibraryManager) -> None:
    """Print a short summary of the current catalog state."""
    books = manager.inventory.all_books()
    for book in sort_books_by_title(books):
        print(f"  - {book}")
    print(f"  Available titles: {manager.inventory.available_titles()}")
    print(f"  Status breakdown: {manager.inventory.status_counts()}")


def run_demo() -> None:
    """Run an end-to-end demonstration of the library system."""
    print(f"=== {LIBRARY_NAME} ===\n")

    manager = LibraryManager()
    seed_catalog(manager)

    print("Catalog on startup:")
    print_catalog_summary(manager)

    student = manager.membership_service.register_student(
        name="ada lovelace", email="ada@example.com", university="MSU Baroda"
    )
    print(f"\nRegistered member: {student} ({student.membership_type.value})")
    print(f"Classification: {manager.membership_service.classify_member(student)}")

    catalog = manager.inventory.all_books()
    isbn_index = build_isbn_index(catalog)
    target_book = isbn_index["9780132350884"]

    try:
        loan = manager.borrow_book(student, target_book.id)
        print(f"\nBorrowed: {target_book.title} -> due {loan.due_date}")
    except LibraryError as exc:
        print(f"Borrow failed: {exc}")
        return

    print(f"Available after borrow: {[b.title for b in available_books(catalog)]}")

    cash = CashPayment(cash_available=50.0)
    fine = manager.return_book(student, target_book.id, payment_method=cash)
    print(f"\nReturned: {target_book.title}, fine charged: ${fine:.2f}")

    print("\nFinal catalog state:")
    print_catalog_summary(manager)


if __name__ == "__main__":
    run_demo()

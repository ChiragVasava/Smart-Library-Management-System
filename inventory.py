"""
inventory.py

Manages the collection of Book objects held by the library.
Demonstrates: for loops, while loops, list/dict comprehensions,
exception raising, type hints, cross-file relationships (models, exceptions).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from exceptions import BookNotAvailableError
from logger import get_logger
from models import Book, BookStatus

logger = get_logger()


class Inventory:
    """Tracks all books owned by the library and their current status."""

    def __init__(self) -> None:
        self._books: Dict[str, Book] = {}

    def add_book(self, book: Book) -> None:
        """Add a new book to the inventory."""
        self._books[book.id] = book
        logger.info("Added book to inventory: %s", book)

    def remove_book(self, book_id: str) -> Optional[Book]:
        """Remove and return a book from the inventory, if present."""
        return self._books.pop(book_id, None)

    def find_by_id(self, book_id: str) -> Optional[Book]:
        """Return the book with the given id, or None if not found."""
        return self._books.get(book_id)

    def find_by_title(self, title: str) -> List[Book]:
        """
        Return all books whose title contains the given substring
        (case-insensitive).

        Demonstrates: for loop, if statement.
        """
        matches: List[Book] = []
        needle = title.lower()
        for book in self._books.values():
            if needle in book.title.lower():
                matches.append(book)
        return matches

    def all_books(self) -> List[Book]:
        """Return every book currently tracked by the inventory."""
        return list(self._books.values())

    def available_titles(self) -> List[str]:
        """
        Return the titles of all currently available books.

        Demonstrates: list comprehension.
        """
        return [book.title for book in self._books.values() if book.available]

    def status_counts(self) -> Dict[str, int]:
        """
        Return a count of books grouped by status.

        Demonstrates: dictionary comprehension combined with a for loop.
        """
        counts: Dict[str, int] = {status.name: 0 for status in BookStatus}
        for book in self._books.values():
            counts[book.status.name] += 1
        return counts

    def checkout(self, book_id: str) -> Book:
        """
        Mark a book as borrowed.

        Raises:
            BookNotAvailableError: if the book does not exist or is
                not currently available.
        """
        book = self._books.get(book_id)
        if book is None or not book.available:
            raise BookNotAvailableError(book_id)
        book.mark_borrowed()
        return book

    def check_in(self, book_id: str) -> Book:
        """
        Mark a book as returned/available again.

        Demonstrates: while loop used for a retry-style consistency check.
        """
        attempts = 0
        book: Optional[Book] = None
        while attempts < 3 and book is None:
            book = self._books.get(book_id)
            attempts += 1
        if book is None:
            raise BookNotAvailableError(book_id)
        book.mark_returned()
        return book

    def bulk_add(self, books: List[Book]) -> int:
        """
        Add multiple books at once.

        Demonstrates: for loop with an accumulator.
        """
        added = 0
        for book in books:
            self.add_book(book)
            added += 1
        return added

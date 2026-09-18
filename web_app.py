"""
web_app.py

FastAPI Web Interface for the Smart Library Management System.
Bridges the existing business logic (LibraryManager, Inventory, Membership, Loan)
to a modern web application accessible at http://localhost:3000.

Used as the Application Under Test (AUT) for TestForge AI-generated Playwright tests.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

from fastapi import FastAPI, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from exceptions import (
    BookNotAvailableError,
    BorrowLimitExceededError,
    LibraryError,
    MembershipExpiredError,
)
from library_manager import LibraryManager
from models import Book, BookStatus, Member, RegularMember

# ---------------------------------------------------------------------------
# FastAPI & Jinja2 Templates Setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Smart Library Management System",
    description="Web Interface for Library Management & TestForge Playwright Testing",
    version="1.0.0",
)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ---------------------------------------------------------------------------
# In-Memory Library State & Demo Seeding
# ---------------------------------------------------------------------------
DEMO_EMAIL = "member@test.com"
DEMO_PASSWORD = "Password123"

manager: LibraryManager = LibraryManager()
member_lookup: Dict[str, Member] = {}


def seed_library_catalog() -> None:
    """Populate the library catalog with standard demo books."""
    global manager, member_lookup

    manager = LibraryManager()
    member_lookup = {}

    # 1. Register default test member
    demo_member = manager.membership_service.register_regular(
        name="member",
        email=DEMO_EMAIL,
    )
    member_lookup[DEMO_EMAIL] = demo_member

    # 2. Add Target Book: The Great Gatsby
    gatsby = Book(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        isbn="9780743273565",
        id="gatsby-001",
        tags=["Classic", "Fiction", "American Literature"],
    )
    manager.inventory.add_book(gatsby)

    # 3. Add Additional Starter Books
    additional_books = [
        Book(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="9780132350884",
            id="clean-001",
            tags=["Software", "Engineering", "Best Practices"],
        ),
        Book(
            title="The Pragmatic Programmer",
            author="Andrew Hunt",
            isbn="9780135957059",
            id="prag-001",
            tags=["Programming", "Career", "Craftsmanship"],
        ),
        Book(
            title="Design Patterns",
            author="Erich Gamma",
            isbn="9780201633610",
            id="dp-001",
            tags=["Architecture", "OOP", "Software Design"],
        ),
        Book(
            title="1984",
            author="George Orwell",
            isbn="9780451524935",
            id="orwell-001",
            tags=["Dystopian", "Classic", "Political Fiction"],
        ),
    ]
    manager.inventory.bulk_add(additional_books)


def reset_demo_state() -> None:
    """Reset the library state to clean initial test state."""
    seed_library_catalog()


# Seed on application load
reset_demo_state()


# ---------------------------------------------------------------------------
# Helper to Resolve Current Member
# ---------------------------------------------------------------------------
def get_current_member(request: Request) -> Member:
    """Resolve member by session cookie, defaulting to demo member."""
    user_email = request.cookies.get("user_email", DEMO_EMAIL)
    member = member_lookup.get(user_email)
    if member is None:
        # If not found, register on the fly as regular member
        member = manager.membership_service.register_regular(
            name=user_email.split("@")[0],
            email=user_email,
        )
        member_lookup[user_email] = member
    return member


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------
class BorrowRequest(BaseModel):
    book_id: str


class ReturnRequest(BaseModel):
    book_id: str


# ---------------------------------------------------------------------------
# Web Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root redirect."""
    user_email = request.cookies.get("user_email")
    if user_email:
        return RedirectResponse(url="/books", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Login page (GET /login).
    Resets the demo state to guarantee clean slate for Playwright test repeatability.
    """
    reset_demo_state()
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "active_page": "login",
            "current_user": None,
            "error": None,
        },
    )


@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Handles user login. Sets user cookie and redirects to /books.
    Accepts demo credentials or any valid member credentials for testing flexibility.
    """
    clean_email = email.strip()

    # For demo & testing, validate password
    if clean_email == DEMO_EMAIL and password != DEMO_PASSWORD:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "active_page": "login",
                "current_user": None,
                "error": "Invalid email or password. Please use demo credentials.",
                "email": clean_email,
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Ensure member exists in service
    if clean_email not in member_lookup:
        new_member = manager.membership_service.register_regular(
            name=clean_email.split("@")[0],
            email=clean_email,
        )
        member_lookup[clean_email] = new_member

    response = RedirectResponse(url="/books", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="user_email",
        value=clean_email,
        max_age=3600 * 24,
        httponly=False,
    )
    return response


@app.get("/logout")
async def logout():
    """Logout handler."""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("user_email")
    return response


@app.get("/books", response_class=HTMLResponse)
async def books_page(request: Request, search: Optional[str] = None):
    """
    Catalog exploration page (GET /books).
    Displays 'Welcome, <user>!' and book cards with 'View Details'.
    Supports server-side search filter as well as client-side dynamic search.
    """
    member = get_current_member(request)
    user_greeting = member.email.split("@")[0]

    all_books = manager.inventory.all_books()

    if search:
        query = search.strip().lower()
        filtered_books = [
            b for b in all_books if query in b.title.lower() or query in b.author.lower()
        ]
    else:
        filtered_books = all_books

    return templates.TemplateResponse(
        request=request,
        name="books.html",
        context={
            "active_page": "books",
            "current_user": member.email,
            "user_greeting": user_greeting,
            "books": filtered_books,
            "search_query": search,
        },
    )


@app.get("/books/{book_id}", response_class=HTMLResponse)
async def book_detail_page(request: Request, book_id: str):
    """
    Book details page (GET /books/{book_id}).
    Displays book details, availability badge, Borrow button,
    confirmation modal, and Return button.
    """
    member = get_current_member(request)
    book = manager.inventory.find_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found in inventory")

    is_borrowed_by_me = book.id in member.borrowed_book_ids

    return templates.TemplateResponse(
        request=request,
        name="book_detail.html",
        context={
            "active_page": "books",
            "current_user": member.email,
            "book": book,
            "is_borrowed_by_me": is_borrowed_by_me,
        },
    )


@app.get("/profile/my-books", response_class=HTMLResponse)
async def my_books_page(request: Request):
    """
    Member profile page displaying borrowed books (GET /profile/my-books).
    Displays heading 'My Borrowed Books' and elements with class 'borrowed-book-card'.
    """
    member = get_current_member(request)
    borrowed_items = []
    for bid in member.borrowed_book_ids:
        b = manager.inventory.find_by_id(bid)
        loan = manager.active_loans.get(bid)
        if b:
            borrowed_items.append({"book": b, "loan": loan})

    return templates.TemplateResponse(
        request=request,
        name="my_books.html",
        context={
            "active_page": "my_books",
            "current_user": member.email,
            "borrowed_books": borrowed_items,
        },
    )


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/borrow")
async def api_borrow_book(payload: BorrowRequest, request: Request):
    """
    API endpoint to borrow a book.
    Executes actual business logic in LibraryManager:
        - Checks membership validity & limits
        - Checks inventory availability
        - Creates Loan record
        - Updates member's active borrowed books
    """
    member = get_current_member(request)
    book = manager.inventory.find_by_id(payload.book_id)
    if not book:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": f"Book '{payload.book_id}' not found."},
        )

    try:
        loan = manager.borrow_book(member, payload.book_id)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Book borrowed successfully!",
                "loan_id": f"{loan.book_id}-{loan.member_id}",
                "due_date": str(loan.due_date),
            },
        )
    except BookNotAvailableError:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "This book is currently unavailable or already borrowed.",
            },
        )
    except BorrowLimitExceededError as exc:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(exc)},
        )
    except MembershipExpiredError as exc:
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": str(exc)},
        )
    except LibraryError as exc:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(exc)},
        )


@app.post("/api/return")
async def api_return_book(payload: ReturnRequest, request: Request):
    """
    API endpoint to return a book.
    Executes actual return workflow in LibraryManager:
        - Restores book status to AVAILABLE
        - Checks fine and processes payment if needed
        - Finalizes return and removes from active loans
    """
    member = get_current_member(request)
    book = manager.inventory.find_by_id(payload.book_id)
    if not book:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": f"Book '{payload.book_id}' not found."},
        )

    try:
        fine = manager.return_book(member, payload.book_id)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Book returned successfully!",
                "fine_charged": fine,
            },
        )
    except LibraryError as exc:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(exc)},
        )


@app.get("/api/reset")
@app.post("/api/reset")
async def api_reset_data():
    """Reset test data back to clean initial state."""
    reset_demo_state()
    return {"status": "ok", "message": "Demo data reset successfully"}


# ---------------------------------------------------------------------------
# Direct Execution Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web_app:app", host="0.0.0.0", port=3000, reload=False)

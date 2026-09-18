# Smart Library Management System — Playwright Testing Context

## 1. Project Purpose
The **Smart Library Management System** is a realistic domain application modeling a community library. It tracks physical books, catalog inventories, tiered member subscriptions (Student, Regular, Premium), lending policies, overdue fines, payment processing, notification dispatching, and audit logging. 

Critically, this project serves as a **"Gold Standard Benchmark / Application Under Test (AUT)"** for **TestForge AI**, an automated testing platform that analyzes Python codebases, extracts AST structures, detects cross-module relationships, and generates end-to-end Playwright tests.

---

## 2. Original Project Type
Originally, the project was a **pure Python backend / CLI application**. It had no HTTP server, web framework, HTML templates, or browser UI. The primary interaction was executing the CLI demonstration via:
```bash
python main.py
```
along with running unit tests in pytest via:
```bash
pytest tests/test_sample.py
```

---

## 3. Original Project Structure
The original codebase consisted of the following files:

- `models.py`: Core domain dataclasses, Enums, and Abstract Base Classes (`BookStatus`, `MembershipType`, `Book`, `Loan`, `Member`, `Student`, `RegularMember`, `PremiumMember`, helper comprehensions `build_isbn_index`, `sort_books_by_title`, `available_books`).
- `inventory.py`: Manages the physical book repository (`Inventory` class), providing lookups by ID, title search, bulk additions, checkout status transitions, and check-in loops.
- `membership.py`: Implements `MembershipService`, responsible for member registration, tier classification (`power-user`, `frequent-borrower`, `standard`, `limited`), and enforcement of borrow limits and subscription expiration.
- `payment.py`: Pluggable payment handling using the Strategy pattern (`PaymentMethod`, `CreditCardPayment`, `CashPayment`, `PaymentProcessor`) with an external mock gateway (`PaymentGateway`) exercising retry mechanisms.
- `notification.py`: Asynchronous dispatching (`NotificationService`, `NotificationChannel`) for email/SMS/push notifications and overdue alerts using `asyncio`.
- `library_manager.py`: Central orchestrator tying together `Inventory`, `MembershipService`, `PaymentProcessor`, and `NotificationService` to implement the end-to-end `borrow_book()` and `return_book()` workflows.
- `utils.py`: Pure helper functions with explicit boundary conditions (`calculate_fine`, `clamp`, `chunk_list`, `group_by_first_letter`, `safe_divide`, `is_valid_isbn`).
- `decorators.py`: Custom decorators including `@admin_required`, execution duration logger `@timed`, and fault-tolerant `@retry`.
- `exceptions.py`: Custom exception hierarchy rooted at `LibraryError`, including `MembershipError`, `MembershipExpiredError`, `BookNotAvailableError`, `BorrowLimitExceededError`, `PaymentError`, `InsufficientFundsError`, and `PaymentGatewayTimeoutError`.
- `logger.py`: Centralized logging configuration with `log_transaction` context manager.
- `constants.py`: Global constants such as `MAX_BOOKS_PER_MEMBER = 5`, `LOAN_PERIOD_DAYS = 14`, `FINE_PER_DAY = 0.50`, etc.
- `main.py`: Runnable CLI script executing an end-to-end simulation of book registration, borrowing, overdue calculation, returning, and catalog summary reporting.
- `tests/test_sample.py`: Hand-written reference test suite covering 12 unit test cases.
- `pytest.ini`: Pytest configuration setting `pythonpath = .` and `testpaths = tests`.
- `requirements.txt`: Initial dependencies containing only `pytest>=8.0.0`.

---

## 4. Original Business Logic
The core business logic of the Smart Library Management System includes:
- **Book**: Represents catalog titles with unique 8-character IDs, titles, authors, ISBNs, and statuses (`AVAILABLE`, `BORROWED`, `RESERVED`, `LOST`).
- **Member Tiers**:
  - `Student`: 50% discount on overdue fines, 5 book borrow limit.
  - `RegularMember`: Standard fees (0% discount), 3 book borrow limit.
  - `PremiumMember`: 100% fine waiver, 10 book borrow limit.
- **Loan**: Tracks loan associations between `book_id` and `member_id`, sets default 14-day due dates, computes overdue day counters, and limits renewals to at most 2.
- **Borrowing (`LibraryManager.borrow_book`)**:
  1. Validates that member account is active and has not exceeded borrow limit.
  2. Verifies that the book is in inventory and currently `AVAILABLE`.
  3. Transitions book status to `BORROWED`.
  4. Creates and registers a new `Loan` object in `active_loans`.
  5. Appends `book_id` to member's `borrowed_book_ids`.
  6. Wraps the transaction in `log_transaction()` and `@timed`.
- **Returning (`LibraryManager.return_book`)**:
  1. Retrieves active loan from `active_loans`.
  2. Calculates fine based on overdue days and member discount tier.
  3. Deducts/charges fine via `PaymentProcessor` if fine > 0.
  4. Calls `inventory.check_in()` to restore book status to `AVAILABLE`.
  5. Asynchronously sends notifications if overdue.
  6. Removes loan and updates member's borrowed list.
- **Inventory Management**: Dictionary-backed repository with title substring search and status count aggregations.

---

## 5. Web Layer Added
To expose a browser-accessible interface compatible with TestForge's Playwright test, a minimal FastAPI web layer was integrated without breaking or rewriting the existing core business logic:

- **Framework**: **FastAPI** with **Jinja2** templating and **Uvicorn** ASGI server.
- **Port Target**: `http://localhost:3000`.
- **Files Created**:
  - `web_app.py`: FastAPI server bridging web routes directly to `LibraryManager`.
  - `templates/base.html`: Modern layout with glassmorphic styling, responsive navigation (`Books`, `My Books`), user profile pills, and modal overlays.
  - `templates/login.html`: Accessible authentication page with email and password inputs, error alert banners, and demo credential helpers.
  - `templates/books.html`: Catalog grid showcasing book cards, real-time dynamic search, and "View Details" action buttons.
  - `templates/book_detail.html`: Book details view featuring availability status badges, 14-day loan parameters, "Borrow" trigger button, modal confirmation dialog, toast alerts, and "Return" state handling.
  - `templates/my_books.html`: Member dashboard rendering active loans inside `div.borrowed-book-card` containers with due date tracking and direct return buttons.
- **State Management & Authentication**:
  - Cookie-based session (`user_email`) linking browser requests directly to registered `Member` instances in `MembershipService`.
  - Deterministic test data initialization and reset hook ensuring test repeatability.

---

## 6. Playwright Test Target
The Playwright script evaluates the full user borrowing workflow end-to-end:
1. **Login**: Navigates to `http://localhost:3000/login`, fills `member@test.com` and `Password123`, clicks `Login`.
2. **Catalog Landing**: Awaits redirect to `/books`, verifies heading `Welcome, member!`.
3. **Book Search**: Locates search input `placeholder="Search books..."`, inputs `"The Great Gatsby"`, presses `Enter`.
4. **Card Inspection**: Asserts card `div.book-card:has-text("The Great Gatsby")` is visible and clicks `View Details`.
5. **Book Details**: Verifies heading `The Great Gatsby` on `/books/*`, verifies `Borrow` button is enabled and clicks it.
6. **Confirmation Modal**: Asserts modal `.confirmation-modal` becomes visible and clicks `Confirm Borrow`.
7. **Success Feedback**: Confirms `.toast-success` displays `"Book borrowed successfully!"`.
8. **State Transition**: Asserts `Borrow` button is hidden and `Return` button is displayed.
9. **Profile Verification**: Clicks link `My Books`, awaits `/profile/my-books`, asserts heading `My Borrowed Books`, and confirms card `div.borrowed-book-card:has-text("The Great Gatsby")` is visible.

---

## 7. Test Data
The application provides pre-seeded demo data:

| Entity | Field | Value |
|---|---|---|
| **Member** | Email | `member@test.com` |
| **Member** | Password | `Password123` |
| **Member** | Type | `RegularMember` (Max: 3 books) |
| **Target Book** | Title | `The Great Gatsby` |
| **Target Book** | Author | `F. Scott Fitzgerald` |
| **Target Book** | ID | `gatsby-001` |
| **Target Book** | ISBN | `9780743273565` |
| **Target Book** | Status | `AVAILABLE` (initially) |
| **Catalog Additions** | Titles | `Clean Code`, `The Pragmatic Programmer`, `Design Patterns`, `1984` |

### Test Data Reset Strategy:
To guarantee that the Playwright test is **100% repeatable** across multiple consecutive runs:
1. Navigating to `GET /login` automatically resets the demo state, restoring `The Great Gatsby` to `AVAILABLE`, clearing active loans, and resetting the demo member's borrowed list.
2. A dedicated API endpoint (`POST /api/reset` / `GET /api/reset`) allows manual or programmatic reset at any time.

---

## 8. Routes

### Web Interface Routes:
- `GET /`: Redirects to `/books` if authenticated, otherwise to `/login`.
- `GET /login`: Renders login view; resets test environment state.
- `POST /login`: Validates credentials, sets `user_email` session cookie, redirects to `/books`.
- `GET /logout`: Clears session cookie and redirects to `/login`.
- `GET /books`: Renders catalog list with search filtering.
- `GET /books/{book_id}`: Renders book detail view with borrow/return controls.
- `GET /profile/my-books`: Renders active member loans.

### REST API Routes:
- `POST /api/borrow`: Accepts `{"book_id": "..."}`, calls `manager.borrow_book(member, book_id)`, returns JSON status.
- `POST /api/return`: Accepts `{"book_id": "..."}`, calls `manager.return_book(member, book_id)`, returns JSON status.
- `GET /api/reset` / `POST /api/reset`: Resets library state to initial seed.

---

## 9. Selectors Used By Playwright

| Element | Selector / Locator in Test | Implemented Element in Web App |
|---|---|---|
| **Login URL** | `expect(page).to_have_url(f"{BASE_URL}/login")` | Route `/login` |
| **Login Heading** | `page.get_by_role("heading", name="Login")` | `<h1>Login</h1>` |
| **Email Input** | `page.fill('input[name="email"]', ...)` | `<input id="email" name="email" type="email" ...>` |
| **Password Input** | `page.fill('input[name="password"]', ...)` | `<input id="password" name="password" type="password" ...>` |
| **Login Button** | `page.get_by_role("button", name="Login")` | `<button type="submit" class="btn ...">Login</button>` |
| **Greeting Message** | `page.get_by_text(f"Welcome, {MEMBER_EMAIL.split('@')[0]}!", exact=False)` | `<h1 class="welcome-title">Welcome, member!</h1>` |
| **Search Input** | `page.get_by_placeholder("Search books...")` | `<input id="search-input" placeholder="Search books..." aria-label="Search books" ...>` |
| **Book Card** | `page.locator(f'div.book-card:has-text("{BOOK_TITLE}")')` | `<div class="book-card" ...><h3 class="book-title">The Great Gatsby</h3>...</div>` |
| **View Details Button** | `book_card.get_by_role("button", name="View Details")` | `<button type="button" class="btn ..." onclick="window.location.href='/books/gatsby-001'">View Details</button>` |
| **Book Detail Heading**| `page.get_by_role("heading", name=BOOK_TITLE)` | `<h1 class="detail-title" id="book-title">The Great Gatsby</h1>` |
| **Borrow Button** | `page.get_by_role("button", name="Borrow")` | `<button type="button" id="borrow-btn" class="btn btn-primary">Borrow</button>` |
| **Confirmation Modal** | `page.locator('.confirmation-modal')` | `<div class="confirmation-modal" id="confirmation-modal-box">...</div>` |
| **Confirm Borrow Button** | `page.get_by_role("button", name="Confirm Borrow")` | `<button type="button" id="confirm-borrow-btn" class="btn btn-success">Confirm Borrow</button>` |
| **Success Toast** | `page.locator('.toast-success')` | `<div id="toast-success-msg" class="toast-success">Book borrowed successfully!</div>` |
| **Success Text** | `expect(success_message).to_have_text("Book borrowed successfully!")` | Exact text content: `"Book borrowed successfully!"` |
| **Return Button** | `page.get_by_role("button", name="Return")` | `<button type="button" id="return-btn" class="btn btn-secondary">Return</button>` |
| **My Books Link** | `page.get_by_role("link", name="My Books")` | `<a href="/profile/my-books" class="nav-link">My Books</a>` |
| **My Books Heading** | `page.get_by_role("heading", name="My Borrowed Books")` | `<h1 class="page-title">My Borrowed Books</h1>` |
| **Borrowed Book Card** | `page.locator(f'div.borrowed-book-card:has-text("{BOOK_TITLE}")')` | `<div class="borrowed-book-card"><h2>The Great Gatsby</h2>...</div>` |

---

## 10. Files Changed

| File Path | Status | Reason for Change |
|---|---|---|
| `web_app.py` | **NEW** | FastAPI server application hosting web routes, REST endpoints, and template rendering on port 3000. |
| `templates/base.html` | **NEW** | Shared layout with responsive navigation, modal styles, and glassmorphic dark theme. |
| `templates/login.html` | **NEW** | Login page with semantic headings, inputs, and accessible Login button. |
| `templates/books.html` | **NEW** | Catalog list with greeting, search box, and book cards matching Playwright selectors. |
| `templates/book_detail.html` | **NEW** | Detail page with Borrow button, confirmation modal dialog, success toast, and Return button. |
| `templates/my_books.html` | **NEW** | Member profile view listing borrowed book cards with active loan metadata. |
| `playwright_tests/test_borrow_book.py` | **NEW** | Verbatim TestForge-generated Playwright test script. |
| `requirements.txt` | **MODIFIED** | Added `fastapi`, `uvicorn`, `jinja2`, `playwright`, and `python-multipart`. |
| `tests/test_borrow_book.py` | **ARCHIVED** | Archived pre-existing draft file (`test_borrow_book.py.legacy_broken_artifact`) which contained an invalid JS regex syntax `/regex/i` that prevented pytest collection. |

---

## 11. Playwright Test Location
The test is located at:
```
playwright_tests/test_borrow_book.py
```
It was **copied exactly and unchanged** from the TestForge specification given in Section 3 of the prompt. No modifications or shortcuts were made to the test logic.

---

## 12. Commands

### Install Dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

### Start Web Application (AUT):
```bash
python -m uvicorn web_app:app --host 0.0.0.0 --port 3000
# or
python web_app.py
```

### Run Playwright E2E Test:
```bash
pytest playwright_tests/test_borrow_book.py -v
```

### Run Existing Reference Unit Tests:
```bash
pytest tests -v
```

### Run Existing CLI Demonstration:
```bash
python main.py
```

---

## 13. Test Execution Result

### Automated Playwright E2E Test:
```
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: ...\Smart Library Management System
configfile: pytest.ini
plugins: anyio-4.15.1
collected 1 item

playwright_tests/test_borrow_book.py::test_borrow_book_successfully PASSED [100%]

============================== 1 passed in 2.25s ==============================
```
- **Result**: **PASSED**
- **Tests**: 1 passed, 0 failed
- **Execution Time**: ~2.25s (subsequent runs), ~5.01s (cold start)

### Existing Reference Unit Tests (`tests/test_sample.py`):
```
============================= test session starts =============================
collected 12 items

tests/test_sample.py::test_book_defaults_to_available PASSED             [  8%]
tests/test_sample.py::test_inventory_checkout_marks_unavailable PASSED   [ 16%]
tests/test_sample.py::test_inventory_checkout_raises_when_unavailable PASSED [ 25%]
tests/test_sample.py::test_borrow_limit_enforced PASSED                  [ 33%]
tests/test_sample.py::test_borrow_and_return_full_flow PASSED            [ 41%]
tests/test_sample.py::test_calculate_fine_boundaries[0-0.0-0.0] PASSED   [ 50%]
tests/test_sample.py::test_calculate_fine_boundaries[-3-0.5-0.0] PASSED  [ 58%]
tests/test_sample.py::test_calculate_fine_boundaries[4-0.0-2.0] PASSED   [ 66%]
tests/test_sample.py::test_calculate_fine_boundaries[4-0.5-1.0] PASSED   [ 75%]
tests/test_sample.py::test_chunk_list_handles_non_divisible_length PASSED [ 83%]
tests/test_sample.py::test_safe_divide_returns_none_on_zero PASSED       [ 91%]
tests/test_sample.py::test_membership_classification PASSED              [100%]

============================= 12 passed in 0.07s ==============================
```

### Existing CLI Demo:
`python main.py` executed successfully, generating the complete transaction trace and catalog breakdown without errors.

---

## 14. Bugs / Problems Encountered

### Problem 1: Broken Pre-Existing Test File in `tests/`
- **Cause**: An earlier draft file `tests/test_borrow_book.py` contained JavaScript regex literal syntax: `expect(locator).to_have_text(/.../i)`. Because Python syntax does not support `/.../i`, running `pytest` failed at collection time with `SyntaxError: invalid syntax`.
- **Fix**: Archived the legacy file to `tests/test_borrow_book.py.legacy_broken_artifact` and placed the valid Python Playwright test into `playwright_tests/test_borrow_book.py`.
- **Verification**: `pytest tests -v` collected and ran all 12 reference tests with 100% success.

### Problem 2: FastAPI Form Processing Dependency Missing
- **Cause**: FastAPI requires `python-multipart` to parse form bodies (`email: str = Form(...)`).
- **Fix**: Installed `python-multipart` and added `python-multipart>=0.0.12` to `requirements.txt`.
- **Verification**: Server booted and processed `POST /login` form submissions without exceptions.

### Problem 3: Starlette Jinja2Templates Signature in Starlette 0.38+
- **Cause**: Calling `templates.TemplateResponse("login.html", {"request": request, ...})` threw `TypeError: cannot use 'tuple' as a dict key (unhashable type: 'dict')` because modern Starlette requires `request: Request` as the first argument: `TemplateResponse(request=request, name="...", context={...})`.
- **Fix**: Updated all `TemplateResponse` calls in `web_app.py` to use `request=request, name=..., context=...`.
- **Verification**: All template endpoints (`/login`, `/books`, `/books/{id}`, `/profile/my-books`) return status code 200.

### Problem 4: Exact Text Matching in Playwright Assertion
- **Cause**: The test calls `expect(success_message).to_have_text("Book borrowed successfully!")`. If any decorative icon (e.g. `✓`) was placed inside `.toast-success`, `to_have_text` would fail due to strict string equality.
- **Fix**: Restricted `.toast-success` to contain exactly `"Book borrowed successfully!"`.
- **Verification**: Playwright assertion passed cleanly.

---

## 15. Generated-Test Assumptions
The TestForge AI generated test makes several specific architectural and DOM assumptions:
1. **URL Paths**: Assumes `/login`, `/books`, `/books/*`, and `/profile/my-books`.
2. **Accessible Names**: Assumes button labels `"Login"`, `"View Details"`, `"Borrow"`, `"Confirm Borrow"`, and `"Return"`, and link label `"My Books"`.
3. **Greeting Syntax**: Assumes user greeting contains `Welcome, {email.split('@')[0]}!`.
4. **Input Selectors**: Assumes input attribute names `name="email"` and `name="password"`.
5. **Search Paradigm**: Assumes placeholder text `"Search books..."` and that pressing `Enter` on the search input keeps the searched title visible.
6. **Card Structures**: Assumes books are wrapped in `div.book-card` and borrowed books in `div.borrowed-book-card`.
7. **Modal Design**: Assumes an overlay container with CSS class `.confirmation-modal`.
8. **Toast Notification**: Assumes a notification element with CSS class `.toast-success` containing exact text `"Book borrowed successfully!"`.
9. **Instant In-Place State Change**: Assumes the `Borrow` button is replaced by a `Return` button on the book detail view without requiring a page navigation.

---

## 16. Known Limitations
- **In-Memory Storage**: State is managed in Python process memory rather than an external SQL/NoSQL database. Server restart resets loans to starter seed.
- **Simplified Password Validation**: In the test environment, passwords other than `Password123` are rejected for `member@test.com`, but complex password hashing (e.g. bcrypt) is omitted to keep the AUT fast and deterministic.
- **Single-Node Execution**: Since state is in-memory, horizontal scaling across multiple Uvicorn worker processes without a shared database is not supported.

---

## 17. Architecture
```
User / Test Runner
       │
       ▼
TestForge AI Platform
       │
       │ Generates Playwright Script
       ▼
Playwright Test (`playwright_tests/test_borrow_book.py`)
       │
       │ HTTP / DOM actions (port 3000)
       ▼
Smart Library Web Layer (`web_app.py` + Jinja2 Templates)
       │
       │ Invokes domain methods
       ▼
Existing Smart Library Business Logic
       │
       ├─► Inventory (`inventory.py`)
       ├─► Membership Service (`membership.py`)
       ├─► Library Manager (`library_manager.py`)
       ├─► Domain Models & Loans (`models.py`)
       ├─► Payment Processor (`payment.py`)
       └─► Notification Service (`notification.py`)
       │
       ▼
In-Memory Application State
```

---

## 18. Interview Explanation
> *"To make this originally CLI-based Python library application testable with TestForge's Playwright test, we introduced a lightweight FastAPI web interface on port 3000 that sits directly on top of the existing business logic. We carefully preserved all original domain models, inventory operations, membership rules, and transaction logging without modifying or bypassing them. We built accessible, responsive HTML templates matching the exact DOM contracts and locators expected by the generated Playwright test, including the login form, catalog search, details view, confirmation modal, and borrowed books profile. To ensure reliable test execution, we implemented a deterministic data reset strategy that starts every test run with a clean state, allowing the Playwright test to pass repeatedly in ~2.25 seconds while keeping the original CLI (`python main.py`) and unit tests fully operational."*

---

## 19. Verification Checklist
- [x] Application starts (`uvicorn web_app:app --host 0.0.0.0 --port 3000`)
- [x] Login works (`GET /login` and `POST /login`)
- [x] Books page works (`GET /books`)
- [x] Search works (`Search books...` with Enter key)
- [x] Book details work (`GET /books/{book_id}`)
- [x] Borrow works (calls `manager.borrow_book`)
- [x] Confirmation works (`.confirmation-modal` dialog)
- [x] Success message works (`.toast-success` with `"Book borrowed successfully!"`)
- [x] Return state works (Borrow hidden, Return visible)
- [x] My Books works (`GET /profile/my-books` displays `div.borrowed-book-card`)
- [x] Playwright test passes (`pytest playwright_tests/test_borrow_book.py -v`)
- [x] Existing CLI still works (`python main.py`)
- [x] Existing tests still work (`pytest tests -v` -> 12 passed)

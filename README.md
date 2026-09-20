# Smart Library Management System

A small "Gold Standard Test Project" — a benchmark codebase purpose-built
to exercise every major Python AST construct that **TestForge AI** needs
to detect, parse, and generate tests for.

It is intentionally realistic (not just data classes) so it also exercises
relationship detection and business-logic-aware test generation.

## Why this project exists

When TestForge AI misbehaves on a real-world codebase, it's hard to tell
whether the bug is in AST parsing, relationship detection, Gemini prompting,
or pytest generation, or is simply a quirk of that particular project.

This project isolates the variable: every language feature it uses is
documented below, so any regression in TestForge AI's output can be traced
straight back to the specific construct that broke.

## Project structure

```
smart_library/
├── models.py            # Dataclasses, Enums, ABCs, inheritance, properties
├── inventory.py          # Book collection management
├── membership.py         # Member registration & borrowing rules
├── payment.py            # ABC payment methods, external gateway, retries
├── notification.py       # Async notification sending
├── library_manager.py    # Orchestrator: the core business logic
├── utils.py               # Boundary-condition-heavy helper functions
├── constants.py           # Global constants
├── decorators.py          # Custom decorators (admin_required, retry, timed)
├── exceptions.py          # Custom exception hierarchy
├── logger.py               # Logging + context manager
├── main.py                 # Runnable end-to-end demo
├── web_app.py              # FastAPI web interface & REST APIs
├── templates/              # Jinja2 HTML templates for Web UI
├── playwright_tests/       # Playwright E2E browser test suites
├── tests/
│   └── test_sample.py     # Small hand-written reference test suite
├── requirements.txt
└── pytest.ini
```

## File relationships

```
                    main.py / web_app.py
                              │
                              ▼
                       LibraryManager
                       /      |      \
                      /       |       \
                     ▼        ▼        ▼
       Inventory   Membership  Payment
             │          │         │
             ▼          ▼         ▼
          Models    Notification  Logger
             │
             ▼
        Exceptions
```

## AST / language features covered

| Feature | Where |
|---|---|
| Imports (cross-file) | every module |
| Dataclasses | `models.py` (`Book`, `Loan`) |
| Enums | `models.py` (`BookStatus`, `MembershipType`), `notification.py` (`NotificationChannel`) |
| Classes & inheritance | `models.py` (`Member` → `Student`/`RegularMember`/`PremiumMember`), `payment.py` (`PaymentMethod` → `CreditCardPayment`/`CashPayment`) |
| Abstract Base Classes | `models.py` (`Member`), `payment.py` (`PaymentMethod`) |
| Decorators (builtin) | `@staticmethod`, `@classmethod`, `@property`, `@dataclass`, `@abstractmethod` |
| Decorators (custom) | `decorators.py` (`admin_required`, `timed`, `retry`) |
| Type hints | throughout (`Optional`, `List`, `Dict`, `Union` via `X | None`) |
| Properties | `models.py` (`Book.available`, `Member.full_name`, `Loan.is_overdue`) |
| Exceptions (custom hierarchy) | `exceptions.py` |
| if / elif / else | `membership.py` (`classify_member`) |
| for loops | `inventory.py`, `library_manager.py` |
| while loops | `inventory.py` (`check_in`), `payment.py` (`pay`) |
| try / except / finally | `payment.py` (`CreditCardPayment.pay`), `utils.py` (`safe_divide`) |
| Nested functions | `membership.py` (`validate_can_borrow._projected_total`), `decorators.py` |
| List comprehensions | `models.py`, `inventory.py`, `library_manager.py` |
| Dictionary comprehensions | `models.py` (`build_isbn_index`), `inventory.py` (`status_counts`) |
| Lambda | `models.py` (`sort_books_by_title`), `utils.py` (`is_valid_isbn`) |
| Async functions | `notification.py` (`send_async`, `notify_overdue`, `notify_many`) |
| Context managers (`with`) | `logger.py` (`log_transaction`, file writes) |
| Logging | `logger.py`, used throughout |
| External/mockable dependency | `payment.py` (`PaymentGateway`) |
| Boundary conditions | `utils.py` (`calculate_fine`, `clamp`, `chunk_list`, `safe_divide`) |
| Business logic chain | `library_manager.py` (`borrow_book`, `return_book`) |

## Business logic flow

```
Borrow Book → Check Membership → Check Inventory → Calculate Fine
→ Process Payment → Send Notification → Log Transaction
```

## Running the Application Locally

### 1. Prerequisites & Installation

Create a virtual environment (optional but recommended) and install dependencies:

```bash
# Create and activate virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

# Install Playwright browser binaries (for automated browser testing)
playwright install chromium
```

### 2. Start the Web Application on Localhost

Run the FastAPI web application on **`http://localhost:3000`**:

```bash
# Option A: Run directly via Python
python web_app.py

# Option B: Run via Uvicorn
python -m uvicorn web_app:app --host 0.0.0.0 --port 3000
```

Once started, open your browser and navigate to:
👉 **[http://localhost:3000](http://localhost:3000)** (or `http://localhost:3000/login`)

#### Demo Login Credentials
- **Email**: `member@test.com`
- **Password**: `Password123`

#### Key Web Features & Endpoints
- **Browse Catalog**: `http://localhost:3000/books` — Real-time search and book cards.
- **Book Details & Borrow**: `http://localhost:3000/books/gatsby-001` — Lending with confirmation modal and status tracking.
- **My Borrowed Books**: `http://localhost:3000/profile/my-books` — View active loans and return books.
- **Reset Test Data**: `http://localhost:3000/api/reset` (Visiting `/login` also resets demo data automatically for repeatable testing).

### 3. Run the CLI Demo

The original CLI workflow remains fully functional:

```bash
python main.py
```

### 4. Running the Tests

```bash
# Run unit & business logic reference test suite
pytest tests -v

# Run Playwright end-to-end browser test against http://localhost:3000
pytest playwright_tests/test_borrow_book.py -v
```

## Using this with TestForge AI

1. Upload the whole `smart_library/` folder (excluding `tests/`, if you
   want to compare generated tests against the hand-written reference
   suite in `tests/test_sample.py`).
2. Verify AST parsing picks up every construct in the table above.
3. Verify relationship detection reconstructs the file-dependency graph
   shown above.
4. Compare TestForge AI's generated tests against `tests/test_sample.py`
   for coverage of the same edge cases (boundary conditions, exceptions,
   retries, async paths).

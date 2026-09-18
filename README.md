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
├── tests/
│   └── test_sample.py     # Small hand-written reference test suite
├── requirements.txt
└── pytest.ini
```

## File relationships

```
                    main.py
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

## Running it

```bash
pip install -r requirements.txt

# Run the end-to-end demo
python main.py

# Run the reference test suite
pytest -v
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

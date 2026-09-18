from playwright.sync_api import sync_playwright, expect
import os

def test_borrow_book_successfully():
    BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
    MEMBER_EMAIL = os.getenv("MEMBER_EMAIL", "member@test.com")
    MEMBER_PASSWORD = os.getenv("MEMBER_PASSWORD", "Password123")
    BOOK_TITLE = os.getenv("BOOK_TITLE", "The Great Gatsby")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(f"{BASE_URL}/login")
            expect(page).to_have_url(f"{BASE_URL}/login")
            expect(page.get_by_role("heading", name="Login")).to_be_visible()

            page.fill('input[name="email"]', MEMBER_EMAIL)
            page.fill('input[name="password"]', MEMBER_PASSWORD)
            page.get_by_role("button", name="Login").click()

            page.wait_for_url(f"{BASE_URL}/books")
            expect(page).to_have_url(f"{BASE_URL}/books")
            expect(page.get_by_text(f"Welcome, {MEMBER_EMAIL.split('@')[0]}!", exact=False)).to_be_visible()

            search_input = page.get_by_placeholder("Search books...") or page.get_by_label("Search books")
            expect(search_input).to_be_visible()
            search_input.fill(BOOK_TITLE)
            page.keyboard.press("Enter")

            page.wait_for_selector(f'text="{BOOK_TITLE}"')
            expect(page.get_by_text(BOOK_TITLE)).to_be_visible()

            book_card = page.locator(f'div.book-card:has-text("{BOOK_TITLE}")')
            expect(book_card).to_be_visible()
            book_card.get_by_role("button", name="View Details").click()

            page.wait_for_url(f"{BASE_URL}/books/*")
            expect(page.get_by_role("heading", name=BOOK_TITLE)).to_be_visible()

            borrow_button = page.get_by_role("button", name="Borrow")
            expect(borrow_button).to_be_visible()
            expect(borrow_button).not_to_be_disabled()
            borrow_button.click()

            confirmation_modal = page.locator('.confirmation-modal')
            expect(confirmation_modal).to_be_visible()
            page.get_by_role("button", name="Confirm Borrow").click()

            success_message = page.locator('.toast-success') or page.get_by_text("Book borrowed successfully!")
            expect(success_message).to_be_visible()
            expect(success_message).to_have_text("Book borrowed successfully!")

            expect(page.get_by_role("button", name="Return")).to_be_visible()
            expect(page.get_by_role("button", name="Borrow")).not_to_be_visible()

            page.get_by_role("link", name="My Books").click()
            page.wait_for_url(f"{BASE_URL}/profile/my-books")
            expect(page.get_by_role("heading", name="My Borrowed Books")).to_be_visible()
            expect(page.locator(f'div.borrowed-book-card:has-text("{BOOK_TITLE}")')).to_be_visible()

        except Exception as e:
            print(f"Test FAILED: {e}")
            page.screenshot(path="borrow_book_failure.png")
            raise
        finally:
            browser.close()

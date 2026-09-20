from playwright.sync_api import sync_playwright, expect
import os

def test_borrow_book_successfully():
    # Externalized Test Data Context
    BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
    MEMBER_EMAIL = os.getenv("MEMBER_EMAIL", "member@test.com")
    MEMBER_PASSWORD = os.getenv("MEMBER_PASSWORD", "Password123") # Assuming a default password for the member
    BOOK_TITLE = os.getenv("BOOK_TITLE", "The Great Gatsby")

    with sync_playwright() as p:
        # Launch browser in headless mode by default, set headless=False for visual debugging
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(10000) # Set a default timeout for all actions and expectations

        try:
            # 1. Login as a valid library member.
            print(f"Navigating to login page: {BASE_URL}/login")
            page.goto(f"{BASE_URL}/login")
            expect(page).to_have_url(f"{BASE_URL}/login")

            print(f"Logging in with email: {MEMBER_EMAIL}")
            page.fill('input[name="email"]', MEMBER_EMAIL)
            page.fill('input[name="password"]', MEMBER_PASSWORD)
            page.click('button[type="submit"]')

            # Assert successful login (e.g., redirect to dashboard and welcome message)
            expect(page).to_have_url(f"{BASE_URL}/books")
            expect(page.locator('h1:has-text("Welcome")')).to_be_visible()
            print("Successfully logged in as library member.")

            # 2. Search for an available book.
            print(f"Navigating to books page: {BASE_URL}/books")
            page.goto(f"{BASE_URL}/books")
            expect(page).to_have_url(f"{BASE_URL}/books")

            print(f"Searching for book: '{BOOK_TITLE}'")
            # Assuming a search input is available on the books listing page
            search_input_locator = page.locator('input[placeholder*="Search books..."]')
            search_input_locator.fill(BOOK_TITLE)
            page.press(search_input_locator.selector, 'Enter') # Submit search by pressing Enter

            # Wait for the search results to reflect the book
            expect(page.locator(f'a:has-text("{BOOK_TITLE}")')).to_be_visible()
            print(f"Book '{BOOK_TITLE}' found in search results.")

            # 3. Select the book.
            # Click on the link or card containing the book title to navigate to its detail page
            page.locator(f'a:has-text("{BOOK_TITLE}")').first.click()

            # Assert we are on the book detail page
            expect(page.locator(f'h1:has-text("{BOOK_TITLE}")')).to_be_visible()
            print(f"Navigated to detail page for '{BOOK_TITLE}'.")

            # 4. Click Borrow.
            print("Clicking 'Borrow' button.")
            borrow_button = page.locator('button:has-text("Borrow")')
            expect(borrow_button).to_be_visible() # Ensure the borrow button is present and visible
            borrow_button.click()

            # 5. Confirm the borrowing action.
            # Assuming a confirmation dialog appears after clicking borrow
            print("Attempting to confirm borrowing action (checking for dialog).")
            confirm_dialog = page.locator('role=dialog') # Locate a generic dialog element
            if confirm_dialog.is_visible():
                print("Confirmation dialog detected. Clicking 'Confirm'.")
                confirm_dialog.locator('button:has-text("Confirm")').click()
            else:
                print("No explicit confirmation dialog found. Assuming direct borrow action.")
            
            # Expected Result Assertions:
            # Success message is displayed.
            success_message_locator = page.locator('text="Book borrowed successfully!"')
            expect(success_message_locator).to_be_visible()
            print("Success message 'Book borrowed successfully!' displayed.")

            # Book is marked as borrowed (e.g., "Return" button instead of "Borrow" or status text).
            # The 'Borrow' button should disappear, and a 'Return' button should appear.
            expect(page.locator('button:has-text("Return")')).to_be_visible()
            expect(page.locator('button:has-text("Borrow")')).not_to_be_visible()
            print(f"Book '{BOOK_TITLE}' is marked as borrowed (Return button visible, Borrow button hidden).")

            # Member's borrowed list is updated.
            print("Navigating to member's 'My Books' section to verify borrowed list.")
            page.click('nav a:has-text("My Books")') # Assuming a navigation link "My Books"
            expect(page).to_have_url(f"{BASE_URL}/my-books") # Assuming the URL for user's borrowed books

            # Verify the book title is present in the list of currently borrowed books
            borrowed_list_item = page.locator(f'section#borrowed-books li:has-text("{BOOK_TITLE}")')
            expect(borrowed_list_item).to_be_visible()
            print(f"Book '{BOOK_TITLE}' is successfully listed in member's borrowed books.")

            print("\nTest 'Borrow Book Successfully' completed successfully!")

        except Exception as e:
            print(f"\nTest FAILED: {e}")
            # Take a screenshot on failure for debugging
            screenshot_path = "borrow_book_failure.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot taken at: {screenshot_path}")
            raise # Re-raise the exception to mark the test as failed

        finally:
            browser.close()
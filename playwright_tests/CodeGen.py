import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:3000/login")
    page.get_by_role("button", name="Login").click()
    page.get_by_role("button", name="View Details").first.click()
    page.get_by_role("button", name="Borrow").click()
    page.get_by_role("button", name="Confirm Borrow").click()
    page.get_by_role("link", name="📚 Smart Library").click()
    page.goto("http://localhost:3000/books")
    page.get_by_role("button", name="View Details").first.click()
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Return").click()
    page.get_by_role("link", name="Back to Catalog").click()
    page.get_by_role("textbox", name="Search books").click()
    page.get_by_role("textbox", name="Search books").fill("The Great Gatsby")
    page.get_by_role("textbox", name="Search books").press("Enter")
    page.get_by_role("button", name="View Details").click()
    page.get_by_role("button", name="Borrow").click()
    page.get_by_role("button", name="Confirm Borrow").click()
    page.get_by_role("link", name="Back to Catalog").click()
    page.get_by_role("button", name="View Details").first.click()
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Return").click()
    page.get_by_role("link", name="Back to Catalog").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

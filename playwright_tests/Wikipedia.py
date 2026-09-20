import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.wikipedia.org/")
    page.get_by_role("link", name="English 7,237,000+ articles").click()
    page.get_by_role("link", name="Central Powers", exact=True).click()
    page.get_by_role("link", name="World War II").click()
    page.get_by_text("Several terms redirect here.").dblclick()
    page.get_by_role("link", name="deaths of 60 to 75 million").click()
    page.get_by_role("link", name="World War II").first.click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

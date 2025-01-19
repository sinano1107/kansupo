from playwright.sync_api import sync_playwright, Page
from dotenv import load_dotenv

load_dotenv()

import os


def login(page: Page):
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
    page.get_by_role("textbox").nth(0).fill(email)
    page.get_by_role("textbox").nth(1).fill(password)
    page.get_by_role("button", name="ログイン").click()
    print("ログインしました")


if __name__ == "__main__":
    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_timeout(20000)
        browser.close()

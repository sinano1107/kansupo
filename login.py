from playwright.sync_api import Page
from dotenv import load_dotenv

load_dotenv()

import os


def login(page: Page):
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
    page.get_by_role("textbox").nth(0).fill(email)
    page.get_by_role("textbox").nth(1).fill(password)
    page.get_by_role("checkbox", name="ログインしたままにする").check()
    page.get_by_role("button", name="ログイン").click()
    page.wait_for_timeout(5000)
    page.context.storage_state(path="login_account.json")
    print("ログインしました")


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_timeout(20000)
        browser.close()

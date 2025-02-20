from playwright.async_api import Page
from dotenv import load_dotenv

from response_receiver import ResponseReceiver

load_dotenv()

import os


async def login(page: Page):
    """環境変数に設定されたアカウントでログインする"""
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    await page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
    await page.get_by_role("textbox").nth(0).fill(email)
    await page.get_by_role("textbox").nth(1).fill(password)
    await page.get_by_role("button", name="ログイン").click()

    # ログイン後のページが表示されるまで待つ
    await ResponseReceiver.expect(
        "http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854"
    )()


if __name__ == "__main__":
    from asyncio import run
    from playwright.async_api import async_playwright

    async def main():
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            page = await browser.new_page()
            await login(page)
            browser.close()

    run(main())

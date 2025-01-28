from typing import Callable
from playwright.sync_api import Playwright, Response


def access(playwright: Playwright, handle_response: Callable[[Response], None]=lambda _: None):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    context = browser.new_context(storage_state="login_account.json")
    page = context.new_page()
    page.on("response", handle_response)
    page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")

    canvas = (
        page.locator('iframe[name="game_frame"]')
            .content_frame.locator("#htmlWrap")
            .content_frame.locator("canvas")
    )

    return canvas

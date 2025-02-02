from typing import Callable
from playwright.sync_api import Playwright, Response, Page


def access(playwright: Playwright, handle_response: Callable[[Response], None]=lambda _: None, handle_prev_access: Callable[[Page], None]=lambda _: None):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    context = browser.new_context(storage_state="login_account.json")
    page = context.new_page()
    
    # ページへのアクセス前に実行する処理
    # .on()を自由につけるために実装
    handle_prev_access(page)
    
    # TODO refactor完了後にこれを消す
    page.on("response", handle_response)
    page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")

    canvas = (
        page.locator('iframe[name="game_frame"]')
            .content_frame.locator("#htmlWrap")
            .content_frame.locator("canvas")
    )

    return canvas

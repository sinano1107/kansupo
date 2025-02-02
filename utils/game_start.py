from typing import Callable
from playwright.async_api import Playwright, Response

from scan.targets.targets import GAME_START_SCAN_TARGET, SETTING_SCAN_TARGET
from utils.click import click
from utils.context import Context
from utils.random_sleep import random_sleep
from utils.wait_until_find import wait_until_find


async def access(playwright: Playwright, handle_response: Callable[[Response], None]):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(
        storage_state="login_account.json",
        viewport={"width": 1300, "height": 900})
    p_page = await context.new_page()
    p_page.on("response", handle_response)
    await p_page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
    canvas = (
        p_page.locator('iframe[name="game_frame"]')
            .content_frame.locator("#htmlWrap")
            .content_frame.locator("canvas")
    )
    return canvas


async def game_start(playwright: Playwright, handle_response: Callable[[Response], None]):
    Context.canvas = await access(playwright, handle_response)
    await wait_until_find(GAME_START_SCAN_TARGET)
    await random_sleep()
    await click(GAME_START_SCAN_TARGET.RECTANGLE)
    await random_sleep()
    await wait_until_find(SETTING_SCAN_TARGET)
    print("ゲームスタート処理を終了しました")
    await random_sleep()
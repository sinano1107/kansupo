import asyncio
from playwright.async_api import async_playwright
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed

from automaton import Automaton
from page_controllers.game_start import GameStartPageController
from response_receiver import ResponseReceiver
from context import Context
from login import login


async def main(headless: bool):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(
            # ボタンが画面外にあるとクリックできないので、canvas要素が全て表示されることを保証するために、viewportを指定する
            viewport={"width": 1300, "height": 900},
        )
        page = await context.new_page()
        page.on("response", ResponseReceiver.handle)
        await page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")

        # ログインする
        await login(page)

        Context.canvas = (
            page.locator('iframe[name="game_frame"]')
            .content_frame.locator("#htmlWrap")
            .content_frame.locator("canvas")
        )

        # ゲームスタートページに遷移するまで待つ(ゲームスタートボタンが表示されるまで)
        game_start_page_controller = await GameStartPageController.sync()
        port_page_controller = await game_start_page_controller.game_start()

        await Automaton(port_page_controller).run()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--retry_count", type=int, default=1)
    args = parser.parse_args()

    retryer = AsyncRetrying(
        stop=stop_after_attempt(args.retry_count), wait=wait_fixed(1), reraise=True
    )
    asyncio.run(retryer(main, args.headless))

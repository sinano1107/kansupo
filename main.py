import asyncio
from playwright.async_api import async_playwright

from page_controllers.game_start import GameStartPageController
from response_receiver import ResponseReceiver
from context import Context


async def main(headless: bool, storage_state: str):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(
            storage_state=storage_state,
            # ボタンが画面外にあるとクリックできないので、canvas要素が全て表示されることを保証するために、viewportを指定する
            viewport={"width": 1300, "height": 900},
        )
        page = await context.new_page()
        page.on("response", ResponseReceiver.handle)
        await page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")

        # storage_stateが指定されていない場合、ログイン画面に遷移しているので、ログインする
        if storage_state is None:
            from tools.login import login

            await login(page)

        Context.canvas = (
            page.locator('iframe[name="game_frame"]')
            .content_frame.locator("#htmlWrap")
            .content_frame.locator("canvas")
        )

        # ゲームスタートページに遷移するまで待つ(ゲームスタートボタンが表示されるまで)
        game_start_page_controller = await GameStartPageController.sync()
        await game_start_page_controller.game_start()

        await asyncio.sleep(10)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--storage_state", type=str)
    args = parser.parse_args()

    asyncio.run(main(headless=args.headless, storage_state=args.storage_state))

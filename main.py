import asyncio
from playwright.async_api import async_playwright

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
        supply_page_controller = await port_page_controller.supply()
        await supply_page_controller.supply(3)
        port_page_controller = await supply_page_controller.port()
        sortie_page_controller = await port_page_controller.sortie()
        mission_page_controller = await sortie_page_controller.mission()
        await mission_page_controller.start(from_the_top=2, fleet_number=3)
        await mission_page_controller.port()

        await asyncio.sleep(10)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    asyncio.run(main(headless=args.headless))

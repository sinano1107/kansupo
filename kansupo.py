from asyncio import Task, create_task, sleep
from playwright.async_api import async_playwright
from logging import getLogger
from fastapi import status
from fastapi.responses import PlainTextResponse

from context import Context
from login import login
from response_receiver import ResponseReceiver


class KanSupo:
    def __init__(self):
        # uvicornを起動するにあたり、loggerはuvicorn.*にしないと表示されない
        self.logger = getLogger("uvicorn.kansupo")
        self.task: Task = None
        self.should_start = False

    def start(self):
        if self.should_start or self.task is not None:
            return PlainTextResponse(
                "すでにプロセスが実行中です",
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        self.logger.info("プロセスを開始します")
        self.should_start = True
        return PlainTextResponse("プロセスを開始しました")

    def stop(self):
        if self.task is None:
            return PlainTextResponse(
                "プロセスが実行されていません",
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        self.logger.info("プロセスを停止します")
        self.task.cancel()
        self.task = None
        return PlainTextResponse("プロセスを停止しました")

    async def run(self, headless: bool):
        from automaton import Automaton

        async def run():
            from page_controllers.game_start import GameStartPageController

            try:
                async with async_playwright() as playwright:
                    browser = await playwright.chromium.launch(headless=headless)
                    context = await browser.new_context(
                        # ボタンが画面外にあるとクリックできないので、canvas要素が全て表示されることを保証するために、viewportを指定する
                        viewport={"width": 1300, "height": 900},
                    )
                    page = await context.new_page()
                    page.on("response", ResponseReceiver.handle)
                    await page.goto(
                        "http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854"
                    )

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
            except Exception as e:
                self.logger.error(e, exc_info=True)
                self.stop()

        while True:
            if self.should_start:
                self.task = create_task(run())
                self.should_start = False
            await sleep(1)


if __name__ == "__main__":
    from asyncio import run
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s,%(msecs)d | %(levelname)s | %(name)s - %(message)s",
    )

    kansupo = KanSupo()
    kansupo.start()
    run(kansupo.run(headless=False))

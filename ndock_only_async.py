import asyncio
from enum import Enum
import json
import operator
from random import random
from typing import Callable, Coroutine
from playwright.async_api import async_playwright, Response, Locator

from rectangle import Rectangle
from targets import GAME_START, HOME_PORT, REPAIR, REPAIR_START, REPAIR_START_CONFIRM, repair_dock_button, repair_ship

class Page(Enum):
    WAITING_START = "WAITING_START"
    START = "START"
    PORT = "PORT"
    NDOCK = "NDOCK"

page: Page = Page.WAITING_START
canvas: Locator = None
handle_in_ndock_page: Callable[[], Coroutine] = lambda: asyncio.sleep(0)

async def random_sleep(base = 1, buffer = 1):
    await asyncio.sleep(base + random() * buffer)

async def click(canvas: Locator, target=Rectangle(x_range=(0, 1200), y_range=(0, 720))):
    x, y = target.random_point()
    await canvas.click(position={"x": x, "y": y})

async def handle_response(res: Response):
    global page
    if res.url == "http://w14h.kancolle-server.com/kcsapi/api_start2/getData":
        print("ゲームスタートに成功しました")
        page = Page.START
    elif res.url == "http://w14h.kancolle-server.com/kcsapi/api_port/port":
        print("母港に到達しました")
        page = Page.PORT
        
        svdata: dict = json.loads((await res.body())[7:])
        data: dict = svdata.get("api_data")
        ndock = data.get("api_ndock")
        
        if ndock[0].get("api_state") == 0:
            print("一番ドックが空いています")
            
            ships = data.get("api_ship")
            ships_of_sorted_by_ndock_time = sorted(filter(lambda ship: ship.get("api_ndock_time") != 0, ships), key=operator.itemgetter("api_ndock_time"))
            if len(ships_of_sorted_by_ndock_time) == 0:
                return
            
            print("入渠の必要がある艦がいます")
            
            await random_sleep(3)
            
            # 次に入渠ページに訪れたときの処理を設定
            async def _handle_in_ndock_page():
                await random_sleep()
                await click(canvas, repair_dock_button(0))
                await random_sleep()
                await click(canvas, repair_ship(0))
                await random_sleep()
                await click(canvas, REPAIR_START)
                await random_sleep()
                await click(canvas, REPAIR_START_CONFIRM)
                await random_sleep()
                await click(canvas, HOME_PORT)
            global handle_in_ndock_page
            handle_in_ndock_page = lambda: _handle_in_ndock_page()
            
            # 入渠ボタンをクリック
            await click(canvas, REPAIR)
    elif res.url == "http://w14h.kancolle-server.com/kcsapi/api_get_member/ndock":
        print("入渠ドックに到達しました")
        page = Page.NDOCK
        await handle_in_ndock_page()
        handle_in_ndock_page = lambda: asyncio.sleep(0)

async def main():
    async with async_playwright() as p:
        global canvas
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="login_account.json")
        p_page = await context.new_page()
        p_page.on("response", handle_response)
        await p_page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
        canvas = (
            p_page.locator('iframe[name="game_frame"]')
                .content_frame.locator("#htmlWrap")
                .content_frame.locator("canvas")
        )
        
        await random_sleep(5, 3)
        while page != Page.PORT:
            await click(canvas, GAME_START)
            await random_sleep()
        
        print("ゲームスタート処理を正常に終了しました")
        await random_sleep()
        
        while True:
            for i in range(4):
                print("\rworking" + "." * i + " " * (3 - i), end="")
                await asyncio.sleep(1)

asyncio.run(main())
import asyncio
from time import time
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, Response

from scan.targets.targets import EXPEDITION_DESTINATION_SELECT_SCAN_TARGET, EXPEDITION_NEXT_SCAN_TARGET, HOME_PORT_SCAN_TARGET, SETTING_SCAN_TARGET, SORTIE_SELECT_SCAN_TARGET
from targets.targets import EXPEDITION_DESTINATION_SELECT_DECIDE, EXPEDITION_DESTINATION_SELECT_TOP, EXPEDITION_SELECT, EXPEDITION_START, FULL_FLEET_SUPPLY, HOME_PORT, REPAIR, SORTIE, SUPPLY
from utils.click import click
from utils.context import Context, ResponseMemory
from utils.game_start import game_start
from utils.page import Page
from utils.random_sleep import random_sleep
from utils.rectangle import Rectangle
from utils.wait_until_find import wait_until_find


async def supply(fleet_num: int = 1):
    if fleet_num < 1 or fleet_num > 4:
        raise ValueError("fleet_numは1以上4以下である必要があります")
    
    await click(SUPPLY)
    await random_sleep()
    
    x_start = 45 * fleet_num + 165
    await click(Rectangle(x_range=(x_start, x_start + 20), y_range=(170, 190), name=f"補給ページの第{fleet_num}艦隊"))
    await random_sleep()
    
    await click(FULL_FLEET_SUPPLY)
    await random_sleep()
    await click(HOME_PORT)
    await wait_until_find(SETTING_SCAN_TARGET)


async def go_expedition():
    print("補給を実施します")
    await supply(2)
    await random_sleep()
    
    print("遠征に送り出します")
    await click(SORTIE)
    await wait_until_find(SORTIE_SELECT_SCAN_TARGET)
    await random_sleep()
    await click(EXPEDITION_SELECT)
    await wait_until_find(EXPEDITION_DESTINATION_SELECT_SCAN_TARGET)
    await random_sleep()
    await click(EXPEDITION_DESTINATION_SELECT_TOP)
    await random_sleep()
    await click(EXPEDITION_DESTINATION_SELECT_DECIDE)
    await random_sleep()
    await click(EXPEDITION_START)
    await asyncio.sleep(2)
    await wait_until_find(HOME_PORT_SCAN_TARGET)
    await random_sleep()
    await click(HOME_PORT)


async def collect_and_go_expedition():
    await click()
    await wait_until_find(EXPEDITION_NEXT_SCAN_TARGET)
    await random_sleep()
    await click()
    await random_sleep()
    await click()
    await wait_until_find(SETTING_SCAN_TARGET)
    await random_sleep()
    await go_expedition()


async def handle_response(res: Response):
    url = res.url
    
    if not url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return
    
    if res.url.endswith("/api_port/port"):
        print("母港に到達しました")
        
        await Context.set_page_and_response(Page.PORT, res)
        
        response = ResponseMemory.port

        # 遠征帰還済みなら、回収して再出発
        if response.deck_list[1].mission[0] == 2:
            print("第2艦隊が遠征から帰投しています")
            async def _():
                await random_sleep()
                await collect_and_go_expedition()
            Context.set_task(_)
            return
        
        # 待機中なら、出発
        if response.deck_list[1].mission[0] == 0:
            print("第2艦隊が待機中のため、遠征に送り出します")
            async def _():
                await random_sleep()
                await go_expedition()
            Context.set_task(_)
            return
        
        # 遠征中/強制帰還中なら待機
        async def reload_and_collect_and_go_expedition():
            wait_seconds = response.deck_list[1].mission[2] / 1000 - time()
            wait_seconds -= 60
            print("{}まで待機してから遠征に送り出します".format(datetime.now() + timedelta(seconds=wait_seconds)))
            await asyncio.sleep(wait_seconds)
            async def _():
                print("遠征帰還時刻になったので、リロード、回収、再出発を実施します")
                await click(REPAIR)
                await random_sleep()
                await click(HOME_PORT)
                await wait_until_find(SETTING_SCAN_TARGET)
                await random_sleep()
                await collect_and_go_expedition()
            Context.set_task(_)
            
        Context.set_wait_task(reload_and_collect_and_go_expedition)


async def main():
    async with async_playwright() as p:
        await game_start(p, handle_response)
        
        while True:
            for i in range(4):
                if Context.task is None:
                    # キューが空の場合は待機
                    print("\rwaiting" + "." * i + " " * (3 - i), end="")
                else:
                    # キューが空でない場合は処理を実行
                    print("\rprocess start!")
                    await Context.do_task()
                # 1秒ごとに確認
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
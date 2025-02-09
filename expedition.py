import asyncio
from time import time
from playwright.async_api import async_playwright, Response

from scan.targets.targets import (
    EXPEDITION_DESTINATION_SELECT_SCAN_TARGET,
    EXPEDITION_NEXT_SCAN_TARGET,
    HOME_PORT_SCAN_TARGET,
    SETTING_SCAN_TARGET,
    SORTIE_SELECT_PAGE_SCAN_TARGET,
)
from targets.targets import (
    EXPEDITION_DESTINATION_SELECT_DECIDE,
    EXPEDITION_DESTINATION_SELECT_TOP,
    EXPEDITION_SELECT,
    EXPEDITION_START,
    HOME_PORT,
    SORTIE,
)
from utils.click import click
from utils.context import Context, ResponseMemory
from utils.game_start import game_start
from utils.page import Page
from utils.random_sleep import random_sleep
from utils.supply import supply
from utils.wait_reload import wait_reload
from utils.wait_until_find import wait_until_find


class DestinationWrapper:
    destination = EXPEDITION_DESTINATION_SELECT_TOP


async def go_expedition():
    print("補給を実施します")
    await supply(2)
    await random_sleep()

    print("遠征に送り出します")
    await click(SORTIE)
    await wait_until_find(SORTIE_SELECT_PAGE_SCAN_TARGET)
    await random_sleep()
    await click(EXPEDITION_SELECT)
    await wait_until_find(EXPEDITION_DESTINATION_SELECT_SCAN_TARGET)
    await random_sleep()
    await click(DestinationWrapper.destination)
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


async def handle_expedition_returned():
    """遠征帰還済みなら、回収して再出発"""
    if ResponseMemory.port.deck_list[1].mission[0] == 2:
        print("第2艦隊が遠征から帰投しています")

        async def _():
            await random_sleep()
            await collect_and_go_expedition()

        Context.set_task(_)
        return True
    return False


async def handle_expedition_idling():
    """遠征待機中なら出発させる"""
    if ResponseMemory.port.deck_list[1].mission[0] == 0:
        print("第2艦隊が待機中のため、遠征に送り出します")

        async def _():
            await random_sleep()
            await go_expedition()

        Context.set_task(_)
        return True
    return False


def calc_expeditions_wait_seconds():
    """遠征帰還時刻までの待機時間を計算"""
    return ResponseMemory.port.deck_list[1].mission[2] / 1000 - time() - 60


async def handle_response(res: Response):
    url = res.url

    if not url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return

    if res.url.endswith("/api_port/port"):
        print("母港に到達しました")
        await Context.set_page_and_response(Page.PORT, res)

        # 遠征帰還済みなら、回収して再出発
        if await handle_expedition_returned():
            return

        # 待機中なら、出発させる
        if await handle_expedition_idling():
            return

        # 遠征中/強制帰還中なら待機
        wait_seconds = calc_expeditions_wait_seconds()
        wait_reload(wait_seconds)


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

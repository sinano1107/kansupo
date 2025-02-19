import asyncio
import math
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
    EXPEDITION_SELECT,
    EXPEDITION_START,
    HOME_PORT,
    SORTIE,
    expedition_destination_from_the_top,
    expedition_fleet,
)
from utils.click import click
from utils.context import Context, PortResponse, ResponseMemory
from utils.game_start import game_start
from utils.page import Page
from utils.random_sleep import random_sleep
from utils.rectangle import Rectangle
from utils.supply import supply
from utils.wait_reload import wait_reload
from utils.wait_until_find import wait_until_find


FLEET_NUM_TO_DESTINATION_MAP = {
    2: expedition_destination_from_the_top(5),
    3: expedition_destination_from_the_top(2),
}


async def go_expedition(fleet_num: int, destination: Rectangle):
    print("補給を実施します")
    await supply(fleet_num=fleet_num)
    await random_sleep()

    # ここで一旦母校に戻るので、他の艦隊の遠征が帰ってきていないか調べる
    # NOTE handle_expedition_returnedと共通部分が多いので、関数にまとめた方がいいかも
    deck_list = ResponseMemory.port.deck_list[1:]
    is_deck_returned_list = [
        deck.mission_state == PortResponse.Deck.MissionState.ExpeditionReturned
        for deck in deck_list
    ]
    if any(is_deck_returned_list):
        for deck, is_deck_returned in zip(deck_list, is_deck_returned_list):
            if not is_deck_returned:
                continue
            print(f"第{deck.id}艦隊が遠征から帰投しているので回収します")
            await collect_returned_expedition()
            await random_sleep()

    print("遠征に送り出します")
    await click(SORTIE)
    await wait_until_find(SORTIE_SELECT_PAGE_SCAN_TARGET)
    await random_sleep()
    await click(EXPEDITION_SELECT)
    await wait_until_find(EXPEDITION_DESTINATION_SELECT_SCAN_TARGET)
    await random_sleep()
    await click(destination)
    await random_sleep()
    await click(EXPEDITION_DESTINATION_SELECT_DECIDE)

    # 第三艦隊、第四艦隊の時は、遠征艦隊を選択
    if fleet_num > 2:
        await random_sleep()
        await click(expedition_fleet(fleet_num))

    await random_sleep()
    await click(EXPEDITION_START)
    await asyncio.sleep(2)
    await wait_until_find(HOME_PORT_SCAN_TARGET)
    await random_sleep()
    await click(HOME_PORT)


async def collect_returned_expedition():
    await click()
    await wait_until_find(EXPEDITION_NEXT_SCAN_TARGET)
    await random_sleep()
    await click()
    await random_sleep()
    await click()
    await wait_until_find(SETTING_SCAN_TARGET)
    await random_sleep()


async def handle_expedition_returned():
    """遠征帰還済みなら、回収して再出発"""
    deck_list = ResponseMemory.port.deck_list[1:]

    is_deck_returned_list = [
        deck.mission_state == PortResponse.Deck.MissionState.ExpeditionReturned
        for deck in deck_list
    ]

    # どの艦隊も遠征から帰投していない場合はブレイク
    if not any(is_deck_returned_list):
        return False

    async def _():
        for deck, is_deck_returned in zip(deck_list, is_deck_returned_list):
            if not is_deck_returned:
                continue
            print(f"第{deck.id}艦隊が遠征から帰投しているので回収します")
            await random_sleep()
            await collect_returned_expedition()

        for deck, is_deck_returned in zip(deck_list, is_deck_returned_list):
            if not is_deck_returned:
                continue
            print(f"第{deck.id}艦隊を遠征に送り出します")
            # go_expeditionの後に設定ボタンを待つ形にすると、タスクが残留し次のタスクを追加できないため、このように前で待つ形としている
            await random_sleep()
            await wait_until_find(SETTING_SCAN_TARGET)
            await random_sleep()
            await go_expedition(
                fleet_num=deck.id,
                destination=FLEET_NUM_TO_DESTINATION_MAP.get(deck.id),
            )

    Context.set_task(_)
    return True


async def handle_expedition_idling():
    """遠征待機中なら出発させる"""
    deck_list = ResponseMemory.port.deck_list[1:]

    is_deck_idling_list = [
        deck.mission_state == PortResponse.Deck.MissionState.NotDispatched
        for deck in deck_list
    ]

    if not any(is_deck_idling_list):
        return False

    async def _():
        for deck, is_deck_idling in zip(deck_list, is_deck_idling_list):
            if not is_deck_idling:
                continue
            print(f"第{deck.id}艦隊が待機中のため、遠征に送り出します。")
            await random_sleep()
            await go_expedition(
                fleet_num=deck.id,
                destination=FLEET_NUM_TO_DESTINATION_MAP.get(deck.id),
            )
            await random_sleep()

    Context.set_task(_)
    return True


def calc_expeditions_wait_seconds():
    """遠征帰還時刻までの待機時間を計算"""
    def calc(micro_seconds: int):
        return micro_seconds / 1000 - time() - 60

    calc_results: list[float] = []
    for deck in ResponseMemory.port.deck_list[1:]:
        if deck.mission_state == PortResponse.Deck.MissionState.OnAnExpedition:
            calc_results.append(calc(deck.mission[2]))

    return min(calc_results) if len(calc_results) > 0 else math.inf


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

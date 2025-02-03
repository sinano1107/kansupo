import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, Response

from battle import handle_sortie
from expedition import (
    calc_expeditions_wait_seconds,
    handle_expedition_idling,
    handle_expedition_returned,
    handle_expedition_waiting,
    DestinationWrapper,
)
from ndock import calc_ndock_data, handle_should_repair, handle_using_all_docks
from scan.targets.targets import HOME_PORT_SCAN_TARGET
from targets.targets import EXPEDITION_DESTINATION_SELECT_5, HOME_PORT, REPAIR
from utils.click import click
from utils.context import Context
from utils.game_start import game_start
from utils.page import Page
from utils.random_sleep import random_sleep
from utils.wait_until_find import wait_until_find


async def handle_response(res: Response):
    url = res.url

    if not url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return

    if res.url.endswith("/api_port/port"):
        print("母港に到達しました")

        if Context.task is not None:
            print("タスクが存在します")
            return

        await Context.set_page_and_response(Page.PORT, res)

        # 遠征帰還済みなら、回収して出発
        if await handle_expedition_returned():
            return

        # 遠征待機中なら出発
        if await handle_expedition_idling():
            return

        # 入渠が必要かつ可能なら入渠を実施
        if await handle_should_repair():
            return

        # 出撃が可能なら出撃
        if await handle_sortie():
            return

        # 最短の遠征が終了するまでの待機秒数を取得
        expeditions_wait_seconds = calc_expeditions_wait_seconds()

        # 最短の入渠が終了するまでの待機秒数と、入渠可能となるドックのインデックスを取得
        repairs_wait_seconds, open_dock_index, using_dock_count = calc_ndock_data()

        # cond値は3分毎に回復するので、最低3分毎にリロードを行う
        reload_period = 3 * 60

        if (
            repairs_wait_seconds is None or repairs_wait_seconds > reload_period
        ) and expeditions_wait_seconds > reload_period:

            async def _():
                print(
                    f"{datetime.now() + timedelta(seconds=reload_period)}まで待ってからリロードを行います"
                )
                await asyncio.sleep(reload_period)

                async def _():
                    await random_sleep()
                    await click(REPAIR)
                    await random_sleep()
                    await wait_until_find(HOME_PORT_SCAN_TARGET)
                    await random_sleep()
                    await click(HOME_PORT)

                await Context.set_task(_)

            Context.set_wait_task(_)
            return

        if repairs_wait_seconds < expeditions_wait_seconds:
            # 入渠が先に終了する場合
            await handle_using_all_docks(
                repairs_wait_seconds, open_dock_index, using_dock_count
            )
            return

        # 遠征が先に終了する場合
        await handle_expedition_waiting(expeditions_wait_seconds)
        return
    elif url.endswith("api_req_map/start"):
        print("出撃開始レスポンスを受け取りました")
        await Context.set_page_and_response(Page.SORTIE_START, res)
    elif url.endswith("/api_req_sortie/battle"):
        print("戦闘開始レスポンスを受け取りました")
        await Context.set_page_and_response(Page.BATTLE, res)
    elif url.endswith("/api_req_battle_midnight/battle"):
        print("夜戦開始レスポンスを受け取りました")
        await Context.set_page_and_response(Page.MIDNIGHT_BATTLE, res)
    elif url.endswith("/api_req_sortie/battleresult"):
        print("戦闘結果レスポンスを受け取りました")
        await Context.set_page_and_response(Page.BATTLE_RESULT, res)
    elif url.endswith("/api_req_map/next"):
        print("次のセルへ向かうレスポンスを受け取りました")
        await Context.set_page_and_response(Page.GOING_TO_NEXT_CELL, res)
    elif url.endswith("/api_get_member/ndock"):
        print("入渠ドックに到達しました")
        Context.set_page(Page.NDOCK)
    else:
        print("ハンドラの設定されていないレスポンスを受け取りました")


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
    DestinationWrapper.destination = EXPEDITION_DESTINATION_SELECT_5
    asyncio.run(main())

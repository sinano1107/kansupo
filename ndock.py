import asyncio
from datetime import datetime, timedelta
from time import time
from playwright.async_api import async_playwright, Response

from utils.context import Context, ResponseMemory
from utils.game_start import game_start
from utils.click import click
from utils.random_sleep import random_sleep
from utils.page import Page
from targets.targets import HOME_PORT, REPAIR, REPAIR_START, REPAIR_START_CONFIRM, repair_dock_button, repair_ship


async def start_repair(should_use_dock_index_list: list[int], repairing_ship_count: int):
    """
    入渠させる処理
    母港画面で実行されることを前提としている
    """
    await random_sleep()

    # 入渠ボタンをクリック
    await click(REPAIR)

    # 入渠ページに遷移するまで待機
    print("入渠ページへ遷移するまで待機します")
    while Context.page != Page.NDOCK:
        await asyncio.sleep(0.1)

    # 入渠ページに到達したら処理を実行
    print("入渠ページに遷移したので、入渠させます")
    await random_sleep()

    for i, dock_index in enumerate(should_use_dock_index_list):
        await click(repair_dock_button(dock_index))
        await random_sleep()

        await click(repair_ship(i + repairing_ship_count))
        await random_sleep()

        await click(REPAIR_START)
        await random_sleep()

        await click(REPAIR_START_CONFIRM)
        await random_sleep()

    await click(HOME_PORT)


async def handle_should_repair():
    """入渠させるべき艦と空きドックがある場合、入渠を開始する"""
    response = ResponseMemory.port
    # 入渠ドックの空き状況を取得
    is_ndock_empty_list = response.ndock_empty_flag_list
    # 入渠させるべき艦のリストを取得
    should_repair_ships = list(
        filter(
            lambda ship: (ship.ndock_time != 0)  # 入渠時間が0の艦は除外
            and (
                ship.id not in response.repairing_ships_id_list
            ),  # すでに入渠中の艦は除外
            response.ship_list,
        )
    )
    # 空きドックの数を取得
    ndock_empty_count = is_ndock_empty_list.count(True)

    # 入渠可能な数が0より大きい場合、入渠を開始する
    can_repair_count = min(ndock_empty_count, len(should_repair_ships))
    if can_repair_count > 0:

        # 使用する入渠ドックのリストを作成する
        index = -1
        should_use_dock_index_list: list[int] = []
        for _ in range(can_repair_count):
            # 前回に発見したTrueの次の要素から検索する
            index = is_ndock_empty_list.index(True, index + 1)
            should_use_dock_index_list.append(index)

        print("入渠を実施します")

        # 入渠させる処理を代入
        Context.set_task(
            lambda: start_repair(
                should_use_dock_index_list,
                repairing_ship_count=[
                    ndock.state for ndock in response.ndock_list
                ].count(1),
            )
        )
        return True
    return False


def calc_ndock_data():
    if ResponseMemory.port.has_repair_ship:
        using_dock_list = [
            dock for dock in ResponseMemory.port.ndock_list if dock.state == 1
        ]
        using_docks_complete_time_list = [
            dock.complete_time for dock in using_dock_list
        ]
        min_complete_time = min(using_docks_complete_time_list)
        open_dock_index = (
            using_dock_list[using_docks_complete_time_list.index(min_complete_time)].id
            - 1
        )

        wait_seconds = min_complete_time / 1000 - time()
        wait_seconds -= 60  # 入渠ページに遷移することで1分短縮できるので、1分引く
        return wait_seconds, open_dock_index, len(using_dock_list)
    return None, None, None


async def handle_using_all_docks(
    wait_seconds: float, min_dock_index: int, using_dock_count: int
):
    print("入渠ドックが空くまで待機します")

    # 待ってから入渠させる処理
    async def wait_and_repair():
        print(
            "{}まで待機してから、入渠させます".format(
                datetime.now() + timedelta(seconds=wait_seconds)
            )
        )
        await asyncio.sleep(wait_seconds)
        print("入渠完了時刻になったので、入渠タスクを代入します")
        Context.task = lambda: start_repair(
            [min_dock_index], repairing_ship_count=using_dock_count - 1
        )

    # 待ってから入渠させる処理のタスクを作成
    Context.set_wait_task(wait_and_repair)


# NOTE 1分未満で入渠が完了する場合にも母港に戻るのがほんの少し時間の無駄
async def handle_response(res: Response):
    if not res.url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return

    if res.url.endswith("/api_port/port"):
        print("母港に到達しました")

        await Context.set_page_and_response(Page.PORT, res)

        if await handle_should_repair():
            return

        wait_seconds, open_dock_index, using_dock_count = calc_ndock_data()

        if wait_seconds is not None:
            await handle_using_all_docks(
                wait_seconds, open_dock_index, using_dock_count
            )
            return

        print("入渠の必要はありません")

    if res.url.endswith("/api_start2/getData"):
        print("getDataのレスポンスを受け取りました")
    elif res.url.endswith("/api_get_member/ndock"):
        print("入渠ドックに到達しました")
        Context.page = Page.NDOCK
    else:
        # FIXME 出撃ページや工廠ページに遷移しても何もレスポンスは帰ってこないので、これだけでは母港ページにいることを保証できない
        print("ハンドラの設定されていないレスポンスを受け取りました")
        Context.cancel_wait_task()


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

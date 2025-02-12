import asyncio
from datetime import datetime
import math
import sys
from playwright.async_api import async_playwright, Response

from battle import SortieDestinationWrapper, handle_sortie
from clean import calc_resource_ships, handle_clean
from expedition import (
    calc_expeditions_wait_seconds,
    handle_expedition_idling,
    handle_expedition_returned,
)
from ndock import calc_repair_wait_seconds, handle_should_repair
from scan.targets.targets import SETTING_SCAN_TARGET
from utils.context import Context, ResponseMemory
from utils.game_start import game_start
from utils.page import Page
from utils.wait_reload import wait_reload
from utils.wait_until_find import wait_until_find


async def handle_response(res: Response):
    url = res.url

    if not url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return

    if res.url.endswith("/api_port/port"):
        # レコードを指示されていたら記録する
        if should_record:
            with open(
                f"{dirname}/port_{int((datetime.now() - start_time).total_seconds())}.txt",
                "w",
            ) as f:
                f.write(await res.text())

        # レスポンスを反映 編成後の編成成功確認/遠征が帰還しているかの確認に用いる
        await ResponseMemory.set_response(Page.PORT, res)

        # 母港画面に訪れるより先に、レスポンスのみが返ることもあるので、母港画面に訪れたことを確認する
        await wait_until_find(SETTING_SCAN_TARGET)

        # ボタン群が出現するまで待機
        await asyncio.sleep(1)

        if Context.task is not None:
            print("タスクが存在します")
            return

        Context.set_page(Page.PORT)

        # 遠征帰還済みなら、回収して出発
        if await handle_expedition_returned():
            return

        # 遠征待機中なら出発
        if await handle_expedition_idling():
            return

        # 入渠が必要かつ可能なら入渠を実施
        resource_ships = calc_resource_ships()
        if await handle_should_repair(resource_ships=resource_ships):
            return

        # 保持艦数が上限に近い場合は解体
        if await handle_clean(resource_ships=resource_ships):
            return

        # 出撃が可能なら出撃
        if await handle_sortie(resource_ships=resource_ships):
            return

        # cond値は3分毎に回復するので、最低3分毎にリロードを行う
        reload_period = 3 * 60 if not Context.skip_sortie else math.inf

        # 最短の遠征が終了するまでの待機秒数を取得
        expeditions_wait_seconds = calc_expeditions_wait_seconds()

        # 最短の入渠が終了するまでの待機秒数と、入渠可能となるドックのインデックスを取得
        repairs_wait_seconds = calc_repair_wait_seconds()

        # cond値の回復、遠征の帰還、入渠完了のいずれかが終了するまで待機しリロード
        wait_reload(min(reload_period, expeditions_wait_seconds, repairs_wait_seconds))
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


async def wait_command():
    while True:
        command = await asyncio.to_thread(input)
        command = command.split(" ")
        if command[0] == "pause":
            if len(command) == 1:
                Context.pause()
                return
            elif len(command) == 2 and command[1] == "sortie":
                Context.skip_sortie = True
                print("出撃を停止します")
                return
        elif command[0] == "resume":
            if len(command) == 1:
                await Context.resume()
            elif len(command) == 2 and command[1] == "sortie":
                Context.skip_sortie = False
                print("出撃を再開します")
            return
        print(f"不明なコマンドです {command=}")


async def main():
    async with async_playwright() as p:
        asyncio.create_task(wait_command())

        await game_start(
            p,
            handle_response,
            record_video_dir=dirname,
        )

        while True:
            await Context.do_task()
            await asyncio.sleep(1)


if __name__ == "__main__":
    global should_record, start_time, dirname
    should_record = "record" in sys.argv
    start_time: datetime = None
    dirname: str = None
    if should_record:
        start_time = datetime.now()
        dirname = "records/main_{}".format(start_time.strftime("%Y%m%d%H%M%S"))
    SortieDestinationWrapper.mapinfo_no = 3
    asyncio.run(main())

import asyncio
from datetime import datetime, timedelta
from enum import Enum
import json
import operator
from random import random
from time import time
from typing import Coroutine
import cv2
import numpy as np
from playwright.async_api import async_playwright, Response, Locator

from rectangle import Rectangle
from scan import ScanTarget
from scan_targets.index import SETTING_SCAN_TARGET
from targets import GAME_START, HOME_PORT, REPAIR, REPAIR_START, REPAIR_START_CONFIRM, repair_dock_button, repair_ship

class Page(Enum):
    START = "START"
    PORT = "PORT"
    NDOCK = "NDOCK"
    # 出撃開始ページ
    SORTIE_START = "SORTIE_START"
    # 戦闘中
    BATTLE = "BATTLE"
    # 夜戦中
    MIDNIGHT_BATTLE = "MIDNIGHT_BATTLE"
    # 戦闘結果
    BATTLE_RESULT = "BATTLE_RESULT"
    # 次のセルへ移動中
    GOING_TO_NEXT_CELL = "GOING_TO_NEXT_CELL"

page: Page = Page.START
canvas: Locator = None
wait_for_dock_to_open_task: asyncio.Task = None
repair: Coroutine = None

async def random_sleep(base: float = 1, buffer: float = 1):
    """ランダムな秒数待つ"""
    await asyncio.sleep(base + random() * buffer)

async def click(canvas: Locator, target=Rectangle(x_range=(0, 1200), y_range=(0, 720))):
    """指定された範囲のランダムな位置をクリックする"""
    x, y = target.random_point()
    await canvas.click(position={"x": x, "y": y})

async def start_repair():
    """
    入渠させる処理
    母港画面で実行されることを前提としている
    """
    
    # 入渠ボタンをクリック
    print("入渠ボタンをクリックします")
    await click(canvas, REPAIR)
    
    # 入渠ページに遷移するまで待機
    print("入渠ページへ遷移するまで待機します")
    while page != Page.NDOCK:
        await asyncio.sleep(0.1)
    
    # 入渠ページに到達したら処理を実行
    print("入渠ページに遷移したので、入居させます")
    await random_sleep()
    
    print("一つ目のドックをクリックします")
    await click(canvas, repair_dock_button(0))
    await random_sleep()
    
    print("一番上の艦をクリックします")
    await click(canvas, repair_ship(0))
    await random_sleep()
    
    print("入渠開始ボタンをクリックします")
    await click(canvas, REPAIR_START)
    await random_sleep()
    
    print("入渠開始確認ボタンをクリックします")
    await click(canvas, REPAIR_START_CONFIRM)
    await random_sleep()
    
    print("母港画面に戻ります")
    await click(canvas, HOME_PORT)
    await random_sleep()
    
    print("母港画面に戻りました")

async def scan(canvas: Locator, targets: list[ScanTarget], log=False) -> int:
    """画面内の指定されたターゲットとの類似度を比較する"""
    screenshot = await canvas.screenshot()
    image = np.frombuffer(screenshot, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    for i, target in enumerate(targets):
        rectangle = target.RECTANGLE
        cropped = image[
            rectangle.Y_RANGE[0] : rectangle.Y_RANGE[1],
            rectangle.X_RANGE[0] : rectangle.X_RANGE[1],
        ]
        # croppedとtarget.IMAGEのサイズは同じ前提なので、類似度は1x1の配列で返ってくる
        similarity = cv2.matchTemplate(cropped, cv2.imread(target.IMAGE), cv2.TM_CCOEFF_NORMED)[0][0]
        if log:
            print("{}番目のターゲットとの類似度は{}です".format(i, similarity))
        if similarity > 0.9:
            return i
    return -1

async def wait_until_find(canvas: Locator, target: ScanTarget, delay=1):
    """指定したターゲットを発見するまで待機する"""
    while True:
        await asyncio.sleep(delay)
        if await scan(canvas, [target]) == 0:
            break

async def handle_response(res: Response):
    if not res.url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return
    
    global page, repair, wait_for_dock_to_open_task
    
    if res.url.endswith("/api_port/port"):
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
            
            # 入渠させる処理を代入
            repair = start_repair
        else:
            print("入渠ドックが埋まっているので待機します")
            complete_time = ndock[0].get("api_complete_time")
            wait_seconds = complete_time / 1000 - time()
            wait_seconds -= 60 # 入渠ページに遷移することで1分短縮できるので、1分引く
            
            # 待ってから入渠させる処理
            async def wait_and_repair():
                global repair
                print("{}まで待機してから、入渠させます".format(datetime.now() + timedelta(seconds=wait_seconds)))
                await asyncio.sleep(wait_seconds)
                print("入渠完了時刻になったので、入渠タスクを代入します")
                repair = start_repair
            
            # 待ってから入渠させる処理のタスクを作成
            # 一応Noneチェックをして、前のタスクが残っていたらキャンセルする
            if wait_for_dock_to_open_task is not None:
                print("前の待機タスクが残っていました。これは不具合の可能性があります。以前のタスクはキャンセルして上書きします。")
                wait_for_dock_to_open_task.cancel()
            wait_for_dock_to_open_task = asyncio.create_task(wait_and_repair())
        return
    
    if res.url.endswith("/api_start2/getData"):
        print("getDataのレスポンスを受け取りました")
    elif res.url.endswith("/api_get_member/ndock"):
        print("入渠ドックに到達しました")
        page = Page.NDOCK
    else:
        # FIXME 出撃ページや工廠ページに遷移しても何もレスポンスは帰ってこないので、これだけでは母港ページにいることを保証できない
        print("ハンドラの設定されていないレスポンスを受け取りました")
        if wait_for_dock_to_open_task is not None:
            print("関係のないページに遷移したので入渠ドックの待機をキャンセルします")
            wait_for_dock_to_open_task.cancel()
            wait_for_dock_to_open_task = None

async def main():
    async with async_playwright() as p:
        global canvas, repair
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="login_account.json", viewport={"width": 1300, "height": 900})
        p_page = await context.new_page()
        p_page.on("response", handle_response)
        await p_page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
        canvas = (
            p_page.locator('iframe[name="game_frame"]')
                .content_frame.locator("#htmlWrap")
                .content_frame.locator("canvas")
        )
        
        await random_sleep(5, 3)
        # スタートページにいる限り、ゲームスタートボタンの位置を定期的にクリックする
        while page == Page.START:
            await click(canvas, GAME_START)
            await random_sleep()
        
        # 右下に設定ボタンが出現するまで待機する
        await wait_until_find(canvas, SETTING_SCAN_TARGET)
        
        print("ゲームスタート処理を終了しました")
        await random_sleep()
        
        while True:
            for i in range(4):
                if repair is None:
                    # キューが空の場合は待機
                    print("\rwaiting" + "." * i + " " * (3 - i), end="")
                else:
                    # キューが空でない場合は処理を実行
                    print("\rprocess start!")
                    await repair()
                    repair = None
                # 1秒ごとに確認
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
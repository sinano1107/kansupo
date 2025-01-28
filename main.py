from dataclasses import dataclass
import json
from queue import Queue
import threading
from time import sleep
from typing import Callable
from playwright.sync_api import sync_playwright, Locator, Response

from access import access
from click import click
from expedition.handle import handle_expedition
from expedition_manage_thread import ExpeditionManageThread
from random_sleep import random_sleep
from scan_targets.index import (
    GAME_START_SCAN_TARGET,
    SETTING_SCAN_TARGET,
)
from sortie.sortie_1_1 import sortie_1_1
from supply import supply
from wait_until_find import wait_until_find


@dataclass
class Ship:
    id: int
    name: str


class MainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        # 艦の情報を格納する辞書
        self.ships: dict[[int]: Ship] = None
        # 優先コマンドを格納するキュー
        self.priority_commands = Queue()
        # コマンドを格納するキュー
        self.commands = Queue()
        # キャンバス要素
        self.canvas: Locator = None

    def run(self):
        with sync_playwright() as playwright:
            def handle_response(res: Response):
                if res.url.startswith("http://w14h.kancolle-server.com/kcsapi/api_start2/getData"):
                    data = json.loads(res.text()[7:])
                    
                    if data.get("api_result") != 1:
                        raise ValueError("getDataAPIが失敗したようです")
                    
                    data = data.get("api_data").get("api_mst_ship")
                    
                    # 駆逐艦イ級以前に味方艦の情報が格納されているので、それのインデックスを取得する
                    end_index = None
                    # 開発時点でのイ級のインデックス以降を探索する
                    for i in range(792, len(data)):
                        if data[i].get("api_id") == 1501:
                            end_index = i
                            break
                    
                    data = data[:end_index]
                    
                    self.ships = { ship.id: ship for ship in [Ship(d.get("api_id"), d.get("api_name")) for d in data]}
                    
                    print("艦の情報を取得しました")
            
            self.canvas = access(playwright, handle_response=handle_response)

            # スタートボタンが出現するまで待機
            print("スタートボタン待機中")
            wait_until_find(self.canvas, GAME_START_SCAN_TARGET)

            random_sleep()

            # スタートボタンをクリック
            print("スタートボタンをクリック")
            click(self.canvas, GAME_START_SCAN_TARGET.RECTANGLE)

            # 設定ボタンが出現(=母港画面に遷移完了)するまで待機
            print("設定ボタン（母港到達）待機中")
            wait_until_find(self.canvas, SETTING_SCAN_TARGET)

            random_sleep()

            print("処理の実行を開始")
            while True:
                if not self.priority_commands.empty():
                    self.priority_commands.get()()
                    random_sleep()
                elif not self.commands.empty():
                    self.commands.get()()
                    random_sleep()
                else:
                    sleep(1)


if __name__ == "__main__":
    with sync_playwright():
        main_thread = MainThread()
        expedition_manage_thread = ExpeditionManageThread(main_thread=main_thread)
        main_thread.start()
        expedition_manage_thread.start()

        try:
            while True:
                try:
                    input_line = input("<コマンドを待機中>\n")
                    command = input_line.split(" ")
                    if command[0] == "sortie":
                        sortie_command: Callable = None

                        if len(command) <= 1 or command[1] == "":
                            print("海域が指定されていません")
                            continue
                        if command[1] == "1-1":
                            sortie_command = lambda: sortie_1_1(main_thread.canvas)
                        else:
                            print("{}は不明な海域です".format(command[1]))
                            continue

                        main_thread.commands.put(sortie_command)
                    elif command[0] == "supply":
                        main_thread.commands.put(lambda: supply(main_thread.canvas))
                    elif command[0] == "expedition":
                        if len(command) <= 1 or command[1] == "":
                            print("遠征先が指定されていません")
                            continue

                        main_thread.commands.put(
                            handle_expedition(
                                command[1],
                                expedition_manage_thread=expedition_manage_thread,
                            )
                        )
                    elif command[0] == "loop":
                        if len(command) <= 1 or command[1] == "":
                            print("ループさせます")
                            expedition_manage_thread.should_loop = True
                        elif command[1] == "stop":
                            print("ループを停止します")
                            expedition_manage_thread.should_loop = False
                        else:
                            print("{} は不明なコマンドです".format(input_line))
                    else:
                        print("{}は不明なコマンドです".format(command[0]))
                except KeyboardInterrupt:
                    break
        finally:
            expedition_manage_thread.save()

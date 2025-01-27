from queue import Queue
import threading
from time import sleep
from typing import Callable
from playwright.sync_api import sync_playwright, Locator

from access import access
from click import click
from random_sleep import random_sleep
from scan_targets.index import (
    EXPEDITION_DESTINATION_SELECT_SCAN_TARGET,
    GAME_START_SCAN_TARGET,
    HOME_PORT_SCAN_TARGET,
    SETTING_SCAN_TARGET,
    SORTIE_SELECT_SCAN_TARGET,
)
from sortie.sortie_1_1 import sortie_1_1
from targets import (
    EXPEDITION_DESTINATION_SELECT_DECIDE,
    EXPEDITION_DESTINATION_SELECT_TOP,
    EXPEDITION_SELECT,
    EXPEDITION_START,
    FULL_FLEET_SUPPLY,
    HOME_PORT,
    SORTIE,
    SUPPLY,
)
from wait_until_find import wait_until_find


class MainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        # コマンドを格納する変数
        self.commands = Queue()
        # キャンバス要素
        self.canvas: Locator = None

    def run(self):
        with sync_playwright() as playwright:
            self.canvas = access(playwright)

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
                if not self.commands.empty():
                    self.commands.get()()
                    random_sleep()
                else:
                    sleep(0.01)


if __name__ == "__main__":
    with sync_playwright():
        main_thread = MainThread()
        main_thread.start()

        while True:
            try:
                command = input("<コマンドを待機中>\n").split(" ")
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
                    def supply():
                        print("補給します")
                        click(main_thread.canvas, SUPPLY)
                        random_sleep()
                        click(main_thread.canvas, FULL_FLEET_SUPPLY)
                        random_sleep()
                        click(main_thread.canvas, HOME_PORT)
                        wait_until_find(main_thread.canvas, SETTING_SCAN_TARGET)

                    main_thread.commands.put(supply)
                elif command[0] == "expedition":
                    expedition_command: Callable = None

                    if len(command) <= 1 or command[1] == "":
                        print("遠征先が指定されていません")
                        continue
                    elif command[1] == "1-1":

                        def expedition_1_1():
                            print("1-1に遠征します")

                            print("出撃ボタンを押します")
                            click(main_thread.canvas, SORTIE)

                            print("出撃ボタンが出るまで待機します")
                            wait_until_find(
                                main_thread.canvas, SORTIE_SELECT_SCAN_TARGET
                            )
                            print("出撃画面が出現しました")

                            random_sleep()

                            print("遠征を選択します")
                            click(main_thread.canvas, EXPEDITION_SELECT)

                            print("遠征先選択画面が出現するまで待機します")
                            wait_until_find(
                                main_thread.canvas,
                                EXPEDITION_DESTINATION_SELECT_SCAN_TARGET,
                            )
                            print("遠征先選択画面が出現しました")

                            random_sleep()

                            print("一番上の海域を選択します")
                            click(main_thread.canvas, EXPEDITION_DESTINATION_SELECT_TOP)

                            random_sleep()

                            print("決定します")
                            click(
                                main_thread.canvas, EXPEDITION_DESTINATION_SELECT_DECIDE
                            )

                            random_sleep()

                            print("遠征開始ボタンを押します")
                            click(
                                main_thread.canvas,
                                EXPEDITION_START,
                            )

                            sleep(2)

                            print("母港ボタンが出現するまで待機します")
                            wait_until_find(main_thread.canvas, HOME_PORT_SCAN_TARGET)
                            print("母港ボタンが出現しました")

                            random_sleep()

                            print("母港ボタンを押します")
                            click(main_thread.canvas, HOME_PORT)
                            wait_until_find(main_thread.canvas, SETTING_SCAN_TARGET)
                            print("母港画面に戻りました")

                        expedition_command = expedition_1_1
                    else:
                        print("{}は不明な遠征先です".format(command[1]))
                        continue

                    main_thread.commands.put(expedition_command)
                else:
                    print("{}は不明なコマンドです".format(command[0]))
            except KeyboardInterrupt:
                break

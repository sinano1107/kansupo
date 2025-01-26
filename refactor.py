from datetime import datetime
import threading
from time import sleep
from typing import Callable
from playwright.sync_api import sync_playwright, Locator

from access import access
from click import click
from random_sleep import random_sleep
from scan import scan
from scan_targets.index import (
    GAME_START_SCAN_TARGET,
    GO_BACK_SCAN_TARGET,
    NEXT_SCAN_TARGET,
    SEA_AREA_SELECT_SCAN_TARGET,
    SETTING_SCAN_TARGET,
    SORTIE_SELECT_SCAN_TARGET,
    SORTIE_START_SCAN_TARGET,
    TAN,
    WITHDRAWAL_SCAN_TARGET,
)
from targets import (
    SEA_AREA_LEFT_TOP,
    SEA_AREA_SELECT_DECIDE,
    SELECT_SINGLE_LINE,
    SORTIE,
)
from wait_until_find import wait_until_find


class MainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        # 実行時に与えられたコマンドを格納する変数
        self.command: Callable = None
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

            print("処理の実行を開始")
            while True:
                if self.command != None:
                    self.command()
                    self.command = None
                else:
                    sleep(0.01)


with sync_playwright():
    main_thread = MainThread()
    main_thread.start()

    while True:
        try:
            command = input("<コマンドを待機中>\n").split(" ")
            if command[0] == "screenshot":
                main_thread.command = lambda: main_thread.canvas.screenshot(
                    path="screenshots/{}.png".format(datetime.now())
                )
            elif command[0] == "sortie":
                sortie_command: Callable = None

                if len(command) <= 1 or command[1] == "":
                    print("海域が指定されていません")
                    continue
                if command[1] == "1-1":

                    def sortie_1_1():
                        print("1-1に出撃します")

                        random_sleep()

                        print("出撃ボタンを押下します")
                        click(main_thread.canvas, SORTIE)

                        print("出撃画面が出現するまで待機します")
                        wait_until_find(main_thread.canvas, SORTIE_SELECT_SCAN_TARGET)
                        print("出撃画面が出現しました")

                        random_sleep()

                        print("出撃を選択します")
                        click(main_thread.canvas, SORTIE_SELECT_SCAN_TARGET.RECTANGLE)

                        print("海域選択画面が出現するまで待機します")
                        wait_until_find(main_thread.canvas, SEA_AREA_SELECT_SCAN_TARGET)
                        print("海域選択画面が出現しました")

                        random_sleep()

                        print("左上の海域を選択します")
                        click(main_thread.canvas, SEA_AREA_LEFT_TOP)

                        random_sleep()

                        print("決定します")
                        click(main_thread.canvas, SEA_AREA_SELECT_DECIDE)

                        print("出撃開始ボタンが出現するまで待機します")
                        wait_until_find(main_thread.canvas, SORTIE_START_SCAN_TARGET)
                        print("出撃開始ボタンが出現しました")

                        random_sleep()

                        print("出撃開始ボタンを押下します")
                        click(main_thread.canvas, SORTIE_START_SCAN_TARGET.RECTANGLE)

                        print("単縦陣選択ボタンが出現するまで待機します")
                        wait_until_find(main_thread.canvas, TAN)
                        print("単縦陣選択ボタンが出現しました")

                        random_sleep()

                        print("単縦陣選択ボタンを押下します")
                        click(main_thread.canvas, SELECT_SINGLE_LINE)
                        print("単縦陣を選択しました")

                        random_sleep()

                        print("戦闘終了まで待機します")
                        wait_until_find(main_thread.canvas, NEXT_SCAN_TARGET)
                        print("戦闘終了しました")

                        random_sleep()

                        print("次へ進みます")
                        click(main_thread.canvas)
                        print("次へ進みました")

                        print("次へボタンが表示されるまで待機します")
                        wait_until_find(main_thread.canvas, NEXT_SCAN_TARGET)
                        print("次へボタンが表示されました")

                        click(main_thread.canvas)

                        print(
                            "帰るボタンが出現(=艦娘ドロップ)、もしくは帰還ボタンが出現するまで待機します"
                        )
                        while True:
                            sleep(1)
                            if scan(main_thread.canvas, GO_BACK_SCAN_TARGET):
                                print("帰るボタンが表示されました")
                                random_sleep()
                                print("クリックします")
                                click(main_thread.canvas)
                                wait_until_find(
                                    main_thread.canvas, WITHDRAWAL_SCAN_TARGET
                                )
                                random_sleep()
                                break
                            elif scan(main_thread.canvas, WITHDRAWAL_SCAN_TARGET):
                                print("撤退ボタンが表示されました")
                                random_sleep()
                                break

                        click(main_thread.canvas, WITHDRAWAL_SCAN_TARGET.RECTANGLE)

                        print("母港に戻るまで待機します")
                        wait_until_find(main_thread.canvas, SETTING_SCAN_TARGET)
                        print("母港に戻りました")

                    sortie_command = sortie_1_1
                else:
                    print("{}は不明な海域です".format(command[1]))
                    continue

                main_thread.command = sortie_command
            else:
                print("{}は不明なコマンドです".format(command[0]))
        except KeyboardInterrupt:
            break

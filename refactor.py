from datetime import datetime
import threading
from time import sleep
from typing import Callable
from playwright.sync_api import sync_playwright, Locator

from access import access
from click import click
from detect_huge_damage import detect_huge_damage
from random_sleep import random_sleep
from scan import scan
from scan_targets.index import (
    COMPASS,
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
    ATTACK,
    FULL_FLEET_SUPPLY,
    HOME_PORT,
    SEA_AREA_LEFT_TOP,
    SEA_AREA_SELECT_DECIDE,
    SELECT_SINGLE_LINE,
    SORTIE,
    SUPPLY,
)
from wait_until_find import wait_until_find, wait_until_find_any


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

            random_sleep()

            print("処理の実行を開始")
            while True:
                if self.command != None:
                    self.command()
                    self.command = None
                    random_sleep()
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

                        sleep(10)

                        print("戦闘終了まで待機します")
                        wait_until_find(main_thread.canvas, NEXT_SCAN_TARGET)
                        print("戦闘終了しました")

                        random_sleep()

                        print("次へ進みます")
                        click(main_thread.canvas)
                        print("次へ進みました")

                        print("次へボタンが表示されるまで待機します")
                        wait_until_find(main_thread.canvas, NEXT_SCAN_TARGET)

                        print("大破艦がいるか確認します")
                        huge_damage = detect_huge_damage(main_thread.canvas)
                        should_withdrawal = len(huge_damage) > 0
                        if should_withdrawal and 0 in huge_damage:
                            print("旗艦が大破しています")
                            print("この場合の処理は未記述のため、処理を終了します")
                            return

                        click(main_thread.canvas)

                        print(
                            "帰るボタンが出現(=艦娘ドロップ)、もしくは帰還ボタンが出現するまで待機します"
                        )
                        res = wait_until_find_any(
                            main_thread.canvas,
                            [GO_BACK_SCAN_TARGET, WITHDRAWAL_SCAN_TARGET],
                        )
                        if res == 0:
                            print("帰るボタンが表示されました")
                            random_sleep()
                            print("クリックします")
                            click(main_thread.canvas)
                            wait_until_find(main_thread.canvas, WITHDRAWAL_SCAN_TARGET)
                            random_sleep()
                        elif res == 1:
                            print("撤退ボタンが表示されました")
                            random_sleep()
                        else:
                            print("不明なケースです\r処理を終了します", res)
                            return

                        if should_withdrawal:
                            print("撤退ボタンをクリックします")
                            click(main_thread.canvas, WITHDRAWAL_SCAN_TARGET.RECTANGLE)

                            print("母港に戻るまで待機します")
                            wait_until_find(main_thread.canvas, SETTING_SCAN_TARGET)
                            print("母港に戻りました")
                            return

                        print("進撃ボタンをクリックします")
                        click(main_thread.canvas, ATTACK)
                        print("進撃ボタンをクリックしました")

                        print("羅針盤出現まで待機します")
                        wait_until_find(main_thread.canvas, COMPASS)
                        print("羅針盤が出現しました")

                        print("クリックします")
                        click(main_thread.canvas)
                        print("クリックしました")

                        print("単縦陣選択ボタンが出現するまで待機します")
                        wait_until_find(main_thread.canvas, TAN)
                        print("単縦陣選択ボタンが出現しました")

                        random_sleep()

                        print("単縦陣選択ボタンを押下します")
                        click(main_thread.canvas, SELECT_SINGLE_LINE)
                        print("単縦陣を選択しました")

                        sleep(10)

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
                        print("次へボタンをクリックしました")

                        print(
                            "帰るボタンか設定ボタンが表示される(=母港へ帰還)まで待機します"
                        )
                        res = wait_until_find_any(
                            main_thread.canvas,
                            [GO_BACK_SCAN_TARGET, SETTING_SCAN_TARGET],
                        )
                        if res == 0:
                            print("帰るボタンが表示されました")
                            random_sleep()
                            print("クリックします")
                            click(main_thread.canvas)
                            print("母港に帰還するまで待機します")
                            wait_until_find(main_thread.canvas, SETTING_SCAN_TARGET)
                            print("母港に帰還しました")
                        elif res == 1:
                            print("母港に帰還しました")
                        else:
                            print("不明なケースです\r処理を終了します", res)
                            return

                    sortie_command = sortie_1_1
                else:
                    print("{}は不明な海域です".format(command[1]))
                    continue

                main_thread.command = sortie_command
            elif command[0] == "supply":

                def supply():
                    print("補給します")
                    click(main_thread.canvas, SUPPLY)
                    random_sleep()
                    click(main_thread.canvas, FULL_FLEET_SUPPLY)
                    random_sleep()
                    click(main_thread.canvas, HOME_PORT)
                    wait_until_find(main_thread.canvas, SETTING_SCAN_TARGET)

                main_thread.command = supply
            else:
                print("{}は不明なコマンドです".format(command[0]))
        except KeyboardInterrupt:
            break

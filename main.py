from datetime import datetime
import threading
from time import sleep
from typing import Callable
from playwright.sync_api import sync_playwright, Locator

from access import access
from click import click
from random_sleep import random_sleep
from scan_targets.index import (
    GAME_START_SCAN_TARGET,
    SETTING_SCAN_TARGET,
)
from sortie.sortie_1_1 import sortie_1_1
from targets import (
    FULL_FLEET_SUPPLY,
    HOME_PORT,
    SUPPLY,
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
                    sortie_command = lambda: sortie_1_1(main_thread.canvas)
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

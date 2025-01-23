from datetime import datetime
from random import random
import threading
from time import sleep
from typing import Callable
from playwright.sync_api import sync_playwright, Locator

from access import access
from scan_targets.index import GAME_START_SCAN_TARGET, SETTING_SCAN_TARGET
from targets import GAME_START
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
            wait_until_find(self.canvas, GAME_START_SCAN_TARGET)

            # 0~5秒待つ
            sleep(random() * 5)

            # スタートボタンをクリック
            x, y = GAME_START.random_point()
            self.canvas.click(position={"x": x, "y": y})

            # 設定ボタンが出現(=母港画面に遷移完了)するまで待機
            wait_until_find(self.canvas, SETTING_SCAN_TARGET)

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
            command = input("<コマンドを待機中>\n")
            if command == "screenshot":
                main_thread.command = lambda: main_thread.canvas.screenshot(
                    path="screenshots/{}.png".format(datetime.now())
                )
        except KeyboardInterrupt:
            break

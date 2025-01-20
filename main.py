from playwright.sync_api import sync_playwright
import threading
import time
import queue
from datetime import datetime
from login import login
from click import click


class ThreadJob(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.kill_flag = False
        self.queue = queue.Queue()
        self.canvas = None

    def run(self):
        with sync_playwright() as playwright:
            chromium = playwright.chromium
            browser = chromium.launch(headless=False)
            page = browser.new_page()

            login(page)

            page.wait_for_timeout(15000)
            self.canvas = (
                page.locator('iframe[name="game_frame"]')
                .content_frame.locator("#htmlWrap")
                .content_frame.locator("canvas")
            )

            self.click(x_range=(700, 1100), y_range=(560, 640))

            page.wait_for_timeout(10000)

            while True:
                if not self.queue.empty():
                    command = self.queue.get()
                    if command == "screenshot":
                        self.screenshot()
                time.sleep(1)

    def click(self, x_range: tuple[float, float], y_range: tuple[float, float]):
        click(self.canvas, x_range, y_range)

    def screenshot(self):
        if self.canvas == None:
            print("canvasがNoneなのでスクリーンショットを取得できません")
        else:
            self.canvas.screenshot(path="screenshots/{}.png".format(datetime.now()))


with sync_playwright() as playwright:
    t = ThreadJob()
    t.start()

    while True:
        command = input()
        if command == "screenshot":
            t.queue.put("screenshot")
            print("screenshotをqueueに追加しました")
        else:
            print("不明なコマンドです {}".format(command))

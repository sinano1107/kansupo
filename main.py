from playwright.sync_api import sync_playwright, Locator
import threading
import time
from queue import Queue
from commands.command import Command
from commands.index import ENABLED_COMMANDS
from login import login
from click import click


class ThreadJob(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.kill_flag = False
        self.queue: Queue[Command] = Queue()
        self.canvas: Locator = None

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
                    command.run(canvas=self.canvas)
                time.sleep(1)

    def click(self, x_range: tuple[float, float], y_range: tuple[float, float]):
        click(self.canvas, x_range, y_range)


with sync_playwright() as playwright:
    t = ThreadJob()
    t.start()
    
    command_dict = { command.get_name(): command for command in ENABLED_COMMANDS }

    while True:
        input_line = input()
        command = command_dict.get(input_line)
        
        if command == None:
            print("不明なコマンドです {}".format(input_line))
        else:
            t.queue.put(command)

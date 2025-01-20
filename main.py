from playwright.sync_api import sync_playwright, Locator
import threading
import time
from queue import Queue
from commands.click import ClickCommand
from commands.command import Command
from commands.index import ENABLED_COMMANDS
from login import login
from targets import GAME_START


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

            ClickCommand(GAME_START).run(canvas=self.canvas)

            page.wait_for_timeout(10000)

            while True:
                if not self.queue.empty():
                    command = self.queue.get()
                    command.run(canvas=self.canvas)
                time.sleep(1)


with sync_playwright() as playwright:
    t = ThreadJob()
    t.start()

    while True:
        input_line = input()
        input_array = input_line.split()
        command_type = ENABLED_COMMANDS.get(input_array[0])
        
        if command_type == None:
            print("不明なコマンドです {}".format(input_line))
        else:
            command = command_type.instantiate(input_array[1:])
            t.queue.put(command)

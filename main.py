from playwright.sync_api import sync_playwright, Locator
import threading
import time
from queue import Queue
from commands.click import ClickCommand
from commands.command import Command
from commands.index import ENABLED_COMMANDS
from commands.wait import WaitCommand
from targets import GAME_START


class ThreadJob(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.pause = False
        self.interrupt_task: function = None
        self.queue: Queue[Command] = Queue()
        self.canvas: Locator = None

    def run(self):
        with sync_playwright() as playwright:
            chromium = playwright.chromium
            browser = chromium.launch(headless=False)
            context = browser.new_context(storage_state="login_account.json")
            page = context.new_page()
            page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
            
            self.canvas = (
                page.locator('iframe[name="game_frame"]')
                .content_frame.locator("#htmlWrap")
                .content_frame.locator("canvas")
            )
            
            WaitCommand(10).run()
            ClickCommand(GAME_START).run(canvas=self.canvas)
            WaitCommand(10).run()

            while True:
                if self.interrupt_task != None:
                    self.interrupt_task()
                    self.interrupt_task = None
                elif not self.pause and not self.queue.empty():
                    command = self.queue.get()
                    command.run(canvas=self.canvas)
                time.sleep(1)


with sync_playwright() as playwright:
    t = ThreadJob()
    t.start()

    while True:
        try:
            input_line = input()
        except KeyboardInterrupt:
            print("終了します")
            exit()
        
        input_array = input_line.split()
        
        if input_array[0] == "pause":
            def pause():
                t.pause = True
                print("中断しました")
            t.interrupt_task = pause
        elif input_array[0] == "resume":
            def resume():
                t.pause = False
                print("再開しました")
            t.interrupt_task = resume
        else:
            command_type = ENABLED_COMMANDS.get(input_array[0])
            
            if command_type == None:
                print("不明なコマンドです {}".format(input_line))
            else:
                try:
                    command = command_type.instantiate(input_array[1:])
                except ValueError as e:
                    print("<エラー発生>")
                    print(e)
                    continue
                t.queue.put(command)

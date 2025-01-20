from typing import Callable
from playwright.sync_api import sync_playwright, Locator
import threading
import time
from queue import Queue
from commands.click import ClickCommand
from commands.command import Command
from commands.index import ENABLED_COMMANDS
from commands.screenshot import ScreenShotCommand
from commands.wait import WaitCommand
from targets import GAME_START


class ThreadJob(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.is_pause = False
        self.interrupt_task: Callable = None
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
            
            WaitCommand(5).run() # 5で最適化済
            ClickCommand(GAME_START).run(canvas=self.canvas)
            WaitCommand(10).run() # 10で最適化済
            
            print("処理を開始します")

            while True:
                if self.interrupt_task != None:
                    self.interrupt_task()
                    self.interrupt_task = None
                elif not self.is_pause and not self.queue.empty():
                    command = self.queue.get()
                    command.run(canvas=self.canvas)
                time.sleep(1)
    
    def pause(self):
        self.is_pause = True
        print("中断しました")
    
    def resume(self):
        self.is_pause = False
        print("再開しました")


with sync_playwright() as playwright:
    t = ThreadJob()
    t.start()
    
    INTERRUPT_COMMANDS: dict[str, Callable] = {
        "pause": t.pause,
        "resume": t.resume,
        "screenshot": lambda: ScreenShotCommand().run(t.canvas)
    }

    while True:
        try:
            input_line = input()
        except KeyboardInterrupt:
            print("終了します")
            exit()
        
        input_array = input_line.split()
        
        # 割り込みコマンド
        interrupt_command = INTERRUPT_COMMANDS.get(input_array[0])
        if interrupt_command != None:
            t.interrupt_task = interrupt_command
            continue
        
        # 通常コマンド
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

# 入渠の自動化のみを行うプログラム

from enum import Enum
from playwright.sync_api import sync_playwright, Response, Page as playwright_Page, Route

from access import access
from click import click
from random_sleep import random_sleep
from targets import GAME_START

class Page(Enum):
    WAITING_START = "WAITING_START"
    START = "START"
    PORT = "PORT"

page: Page = Page.WAITING_START

if __name__ == "__main__":
    with sync_playwright() as p:
        def attach_handler(page: playwright_Page):
            def handle_response(res: Response):
                global page
                if res.url == "http://w14h.kancolle-server.com/kcsapi/api_start2/getData":
                    print("ゲームスタートに成功しました")
                    page = Page.START
            page.on("response", handle_response)
        
        canvas = access(p, handle_prev_access=attach_handler)
        
        # ゲームスタートボタンをクリックする
        random_sleep(5, 3)
        while page == Page.WAITING_START:
            print("クリックします")
            click(canvas, GAME_START)
            random_sleep()
        
        while True:
            command = input()
            print(command)

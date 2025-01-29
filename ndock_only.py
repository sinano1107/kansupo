# 入渠の自動化のみを行うプログラム

from enum import Enum
from playwright.sync_api import sync_playwright, Response, Page as playwright_Page, Route
from time import sleep

from access import access
from click import click
from random_sleep import random_sleep
from targets import GAME_START

class Page(Enum):
    WAITING_START = "WAITING_START"
    START = "START"
    PORT = "PORT"

if __name__ == "__main__":
    with sync_playwright() as p:
        page: Page = Page.WAITING_START
        
        def attach_handler(page: playwright_Page):
            def handle_response(res: Response):
                global page
                if res.url == "http://w14h.kancolle-server.com/kcsapi/api_start2/getData":
                    print("ゲームスタートに成功しました")
                    page = Page.START
                elif res.url == "http://w14h.kancolle-server.com/kcsapi/api_port/port":
                    print("母港に到達しました")
                    page = Page.PORT
            page.on("response", handle_response)
        
        canvas = access(p, handle_prev_access=attach_handler)
        
        # ゲームスタートボタンをクリックする
        random_sleep(5, 3)
        while page == Page.WAITING_START:
            click(canvas, GAME_START)
            random_sleep()
        
        # 母港到達まで待機します
        while page == Page.START:
            sleep(0.1)
        random_sleep()
        
        print("ゲームスタート処理を正常に終了しました")
        
        while True:
            command = input()
            print(command)

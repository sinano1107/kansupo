from datetime import datetime, timedelta
import threading
from time import sleep

from click import click
from random_sleep import random_sleep
from scan import scan
from scan_targets.index import (
    EXPEDITION_NEXT_SCAN_TARGET,
    EXPEDITION_RETURN_MESSAGE,
    SETTING_SCAN_TARGET,
)

from typing import TYPE_CHECKING

from targets import HOME_PORT, SUPPLY
from wait_until_find import wait_until_find

if TYPE_CHECKING:
    from main import MainThread


class ExpeditionManageThread(threading.Thread):
    def __init__(self, main_thread: "MainThread"):
        threading.Thread.__init__(self, daemon=True)
        # メインスレッドのインスタンスを格納する変数
        self.MAIN_THREAD = main_thread
        # 出撃中の遠征の終了時刻を格納する変数
        self.end_time: datetime = None

    def run(self):
        while True:
            if self.end_time is not None and self.end_time <= datetime.now():

                def check_res():
                    print("母港画面にいることを確認します")
                    wait_until_find(self.MAIN_THREAD.canvas, SETTING_SCAN_TARGET)

                    random_sleep()

                    if scan(self.MAIN_THREAD.canvas, [EXPEDITION_RETURN_MESSAGE]) != 0:
                        print("遠征帰還メッセージが表示されていないためリロードします")
                        click(self.MAIN_THREAD.canvas, SUPPLY)
                        random_sleep()
                        click(self.MAIN_THREAD.canvas, HOME_PORT)
                        random_sleep()
                        if (
                            scan(self.MAIN_THREAD.canvas, [EXPEDITION_RETURN_MESSAGE])
                            != 0
                        ):
                            print("帰還していないようなので終了します")
                            # 帰還回収失敗することがあればここの処理を考える
                            return

                    print("画面をクリックして遠征帰還処理を開始します")
                    click(self.MAIN_THREAD.canvas)

                    print("次へボタンが表示されるまで待機します")
                    wait_until_find(
                        self.MAIN_THREAD.canvas, EXPEDITION_NEXT_SCAN_TARGET
                    )
                    print("次へボタンが表示されました")

                    random_sleep()

                    click(self.MAIN_THREAD.canvas)
                    random_sleep()
                    click(self.MAIN_THREAD.canvas)

                    print("母港画面に戻るまで待機します")
                    wait_until_find(self.MAIN_THREAD.canvas, SETTING_SCAN_TARGET)
                    print("母港画面に戻りました")

                self.MAIN_THREAD.commands.put(check_res)
                self.end_time = None
            # 10秒ごとにチェック
            sleep(10)

    # このminutesは遠征にかかる時間を代入する
    def set_end_time(self, minutes: int):
        # 40分の遠征は39分で帰還するので、-1している
        self.end_time = datetime.now() + timedelta(minutes=minutes - 1)
        print("遠征の帰還予定時刻は{}です".format(self.end_time))

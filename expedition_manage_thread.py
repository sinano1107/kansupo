from copy import copy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import threading
from time import sleep

from dataclasses_json import dataclass_json

from click import click
from expedition.handle import handle_expedition
from random_sleep import random_sleep
from scan import scan
from scan_targets.index import (
    EXPEDITION_NEXT_SCAN_TARGET,
    EXPEDITION_RETURN_MESSAGE,
    SETTING_SCAN_TARGET,
    SORTIE_SELECT_SCAN_TARGET,
)

from typing import TYPE_CHECKING

from targets import HOME_PORT, SORTIE
from wait_until_find import wait_until_find

if TYPE_CHECKING:
    from main import MainThread


@dataclass_json
@dataclass(frozen=True)
class ExpeditioningData:
    name: str
    end_time: datetime


class ExpeditionManageThread(threading.Thread):
    SHOULD_ROOP = True
    DELAY = 10
    SAVE_DATA_PATH = "save_data/expedition.txt"

    def __init__(self, main_thread: "MainThread"):
        threading.Thread.__init__(self, daemon=True)
        # メインスレッドのインスタンスを格納する変数
        self.MAIN_THREAD = main_thread
        # 出撃中の遠征の情報を格納する変数
        self.expeditioning_data: ExpeditioningData = None
        # セーブデータの読み込み
        self.load()

    def run(self):
        while True:
            if (
                self.expeditioning_data is not None
                and self.expeditioning_data.end_time
                <= datetime.now(timezone(timedelta(hours=9)))
            ):

                def check_res(name: str):
                    print("母港画面にいることを確認します")
                    wait_until_find(self.MAIN_THREAD.canvas, SETTING_SCAN_TARGET)

                    random_sleep()

                    while True:
                        if (
                            scan(self.MAIN_THREAD.canvas, [EXPEDITION_RETURN_MESSAGE])
                            != 0
                        ):
                            print(
                                "遠征帰還メッセージが表示されていないためリロードします"
                            )
                            click(self.MAIN_THREAD.canvas, SORTIE)
                            wait_until_find(
                                self.MAIN_THREAD.canvas, SORTIE_SELECT_SCAN_TARGET
                            )
                            random_sleep()
                            click(self.MAIN_THREAD.canvas, HOME_PORT)
                            wait_until_find(
                                self.MAIN_THREAD.canvas, SETTING_SCAN_TARGET
                            )
                            random_sleep()
                        else:
                            break

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

                    if self.SHOULD_ROOP:
                        print("ループします")
                        self.MAIN_THREAD.priority_commands.put(
                            handle_expedition(name, self)
                        )

                name = copy(self.expeditioning_data.name)
                self.MAIN_THREAD.priority_commands.put(lambda: check_res(name))
                self.expeditioning_data = None
            # DELAY秒ごとにチェック
            sleep(self.DELAY)

    def save(self):
        if self.expeditioning_data is not None:
            print("帰還待機中の遠征の情報を保存します")
            with open(self.SAVE_DATA_PATH, "w") as f:
                data = self.expeditioning_data.to_json(
                    indent=4,
                )
                f.write(data)

    def load(self):
        try:
            with open(self.SAVE_DATA_PATH, "r") as f:
                data = f.read()
                if data != "":
                    self.expeditioning_data = ExpeditioningData.from_json(data)
                    print("セーブデータをロードしました", self.expeditioning_data)
            with open(self.SAVE_DATA_PATH, "w") as f:
                f.write("")
        except FileNotFoundError:
            print("セーブデータが存在しません")

    # このminutesは遠征にかかる時間を代入する
    def start_wait(self, name: str, minutes: int):
        self.expeditioning_data = ExpeditioningData(
            name=name,
            # 40分の遠征は39分で帰還するので、-1している
            # 回収タスクの追加前に帰還して、他のタスクのクリックによって回収されないように、さらにDELAY*2秒前に設定している。
            end_time=datetime.now(timezone(timedelta(hours=9)))
            + timedelta(minutes=minutes - 1, seconds=-self.DELAY * 2),
        )
        print(
            "遠征{}の帰還予定時刻は{}です".format(
                self.expeditioning_data.name,
                self.expeditioning_data.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )

from time import sleep
from typing import TYPE_CHECKING
from click import click
from playwright.sync_api import Locator
from random_sleep import random_sleep
from scan_targets.index import (
    EXPEDITION_DESTINATION_SELECT_SCAN_TARGET,
    HOME_PORT_SCAN_TARGET,
    SETTING_SCAN_TARGET,
    SORTIE_SELECT_SCAN_TARGET,
)
from supply import supply
from targets import (
    EXPEDITION_DESTINATION_SELECT_DECIDE,
    EXPEDITION_DESTINATION_SELECT_TOP,
    EXPEDITION_SELECT,
    EXPEDITION_START,
    HOME_PORT,
    SORTIE,
)
from wait_until_find import wait_until_find

if TYPE_CHECKING:
    from expedition_manage_thread import ExpeditionManageThread


def expedition_1_1(canvas: Locator, expedition_manage_thread: "ExpeditionManageThread"):
    print("1-1に遠征します")

    supply(canvas, 2)

    print("出撃ボタンを押します")
    click(canvas, SORTIE)

    print("出撃ボタンが出るまで待機します")
    wait_until_find(canvas, SORTIE_SELECT_SCAN_TARGET)
    print("出撃画面が出現しました")

    random_sleep()

    print("遠征を選択します")
    click(canvas, EXPEDITION_SELECT)

    print("遠征先選択画面が出現するまで待機します")
    wait_until_find(
        canvas,
        EXPEDITION_DESTINATION_SELECT_SCAN_TARGET,
    )
    print("遠征先選択画面が出現しました")

    random_sleep()

    print("一番上の海域を選択します")
    click(
        canvas,
        EXPEDITION_DESTINATION_SELECT_TOP,
    )

    random_sleep()

    print("決定します")
    click(
        canvas,
        EXPEDITION_DESTINATION_SELECT_DECIDE,
    )

    random_sleep()

    print("遠征開始ボタンを押します")
    click(
        canvas,
        EXPEDITION_START,
    )

    sleep(2)

    print("母港ボタンが出現するまで待機します")
    wait_until_find(canvas, HOME_PORT_SCAN_TARGET)
    print("母港ボタンが出現しました")

    expedition_manage_thread.start_wait("1-1", 15)

    random_sleep()

    print("母港ボタンを押します")
    click(canvas, HOME_PORT)
    wait_until_find(canvas, SETTING_SCAN_TARGET)
    print("母港画面に戻りました")

from time import sleep
from typing import TYPE_CHECKING
from legacy.click import click
from expedition.destinations import ExpeditionDestination
from legacy.random_sleep import random_sleep
from scan.targets.targets import (
    EXPEDITION_DESTINATION_SELECT_SCAN_TARGET,
    HOME_PORT_SCAN_TARGET,
    SETTING_SCAN_TARGET,
    SORTIE_SELECT_SCAN_TARGET,
)
from legacy.supply import supply
from targets import (
    EXPEDITION_DESTINATION_SELECT_DECIDE,
    EXPEDITION_SELECT,
    EXPEDITION_START,
    HOME_PORT,
    SORTIE,
)
from legacy.wait_until_find import wait_until_find

if TYPE_CHECKING:
    from legacy.expedition_manage_thread import ExpeditionManageThread


def go_expedition(
    expedition_manage_thread: "ExpeditionManageThread",
    destination: ExpeditionDestination,
):
    canvas = expedition_manage_thread.MAIN_THREAD.canvas

    print("{}に遠征します".format(destination.name))

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

    # 遠征先クラスに移譲
    destination.select(canvas)

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

    expedition_manage_thread.start_wait(destination.name, destination.minutes)

    random_sleep()

    print("母港ボタンを押します")
    click(canvas, HOME_PORT)
    wait_until_find(canvas, SETTING_SCAN_TARGET)
    print("母港画面に戻りました")

from scan.targets.targets import SETTING_SCAN_TARGET
from targets.targets import FULL_FLEET_SUPPLY, HOME_PORT, SUPPLY
from utils.click import click
from utils.random_sleep import random_sleep
from utils.rectangle import Rectangle
from utils.wait_until_find import wait_until_find


async def supply(fleet_num: int = 1):
    if fleet_num < 1 or fleet_num > 4:
        raise ValueError("fleet_numは1以上4以下である必要があります")

    await click(SUPPLY)
    await random_sleep()

    x_start = 45 * fleet_num + 165
    await click(Rectangle(x_range=(x_start, x_start + 20), y_range=(170, 190), name=f"補給ページの第{fleet_num}艦隊"))
    await random_sleep()

    await click(FULL_FLEET_SUPPLY)
    await random_sleep(2)
    await click(HOME_PORT)
    await wait_until_find(SETTING_SCAN_TARGET)

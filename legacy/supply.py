from playwright.async_api import Locator
from legacy.click import click
from legacy.random_sleep import random_sleep
from rectangle import Rectangle
from scan_targets.index import SETTING_SCAN_TARGET
from targets import FULL_FLEET_SUPPLY, HOME_PORT, SUPPLY
from legacy.wait_until_find import wait_until_find


def supply(canvas: Locator, fleet_num: int = 1):
    print("補給します")
    click(canvas, SUPPLY)
    random_sleep()

    if fleet_num > 1:
        x_start = 45 * fleet_num + 165
        click(canvas, Rectangle(x_range=(x_start, x_start + 20), y_range=(170, 190)))
        random_sleep()

    click(canvas, FULL_FLEET_SUPPLY)
    random_sleep()
    click(canvas, HOME_PORT)
    wait_until_find(canvas, SETTING_SCAN_TARGET)

from playwright.async_api import Locator
from click import click
from random_sleep import random_sleep
from scan_targets.index import SETTING_SCAN_TARGET
from targets import FULL_FLEET_SUPPLY, HOME_PORT, SUPPLY
from wait_until_find import wait_until_find


def supply(canvas: Locator):
    print("補給します")
    click(canvas, SUPPLY)
    random_sleep()
    click(canvas, FULL_FLEET_SUPPLY)
    random_sleep()
    click(canvas, HOME_PORT)
    wait_until_find(canvas, SETTING_SCAN_TARGET)

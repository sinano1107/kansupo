from time import sleep
from playwright.sync_api import Locator

from scan import scan, ScanTarget


def wait_until_find(canvas: Locator, target: ScanTarget, delay=1):
    while True:
        sleep(delay)
        if scan(canvas, target):
            break

from time import sleep
from playwright.sync_api import Locator

from legacy.scan import scan, ScanTarget


def wait_until_find(canvas: Locator, target: ScanTarget, delay=1):
    while True:
        sleep(delay)
        if scan(canvas, targets=[target]) == 0:
            break


def wait_until_find_any(canvas: Locator, targets: list[ScanTarget], delay=1):
    while True:
        sleep(delay)
        scan_result = scan(canvas, targets)
        if scan_result > -1:
            return scan_result

import asyncio
from playwright.async_api import Locator

from scan.scan import scan
from scan.scan_target import ScanTarget


async def wait_until_find(canvas: Locator, target: ScanTarget, delay=1):
    """指定したターゲットを発見するまで待機する"""
    while True:
        await asyncio.sleep(delay)
        if await scan(canvas, [target]) == 0:
            break
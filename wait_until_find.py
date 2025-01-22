import asyncio
from playwright.async_api import Locator

from scan import scan, ScanTarget


async def wait_until_find(canvas: Locator, target: ScanTarget, delay = 1):
    while True:
        await asyncio.sleep(delay)
        if await scan(canvas, target):
            break
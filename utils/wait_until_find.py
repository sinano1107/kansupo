import asyncio
from playwright.async_api import Locator

from scan.scan import scan
from scan.scan_target import ScanTarget


async def wait_until_find(canvas: Locator, target: ScanTarget, delay=1):
    """指定したターゲットを発見するまで待機する"""
    name = "ターゲット" if target.name is None else target.name
    print(f"{name}が表示されるまで待機します")
    while True:
        await asyncio.sleep(delay)
        if await scan(canvas, [target]) == 0:
            break
    print(f"{name}が表示されました")
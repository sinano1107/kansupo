import asyncio

from scan.scan import scan
from scan.scan_target import ScanTarget
from utils.context import Context


# TODO ファイル名をwait_until.pyにする


async def wait_until_find(target: ScanTarget, delay=1):
    """指定したターゲットを発見するまで待機する"""
    name = "ターゲット" if target.name is None else target.name
    print(f"{name}が表示されるまで待機します")
    while True:
        await asyncio.sleep(delay)
        if await scan(Context.canvas, [target]) == 0:
            break
    print(f"{name}が表示されました")


async def wait_until_lost(target: ScanTarget, delay=1):
    """指定したターゲットが消えるまで待機する"""
    name = "ターゲット" if target.name is None else target.name
    print(f"{name}が消えるまで待機します")
    while True:
        await asyncio.sleep(delay)
        if await scan(Context.canvas, [target]) == -1:
            break
    print(f"{name}が消えました")

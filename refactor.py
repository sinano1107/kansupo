import asyncio
from random import random
from playwright.async_api import async_playwright, Playwright

from access import access
from scan_targets.index import GAME_START_SCAN_TARGET
from targets import GAME_START
from wait_until_find import wait_until_find


async def run(playwright: Playwright):
    canvas = await access(playwright)

    # 1秒ごとにスタートボタンが出現したかを確認する
    await wait_until_find(canvas, GAME_START_SCAN_TARGET)

    # 0~5秒待つ
    await asyncio.sleep(random() * 5)

    # スタートボタンをクリック
    x, y = GAME_START.randam_point()
    await canvas.click(position={"x": x, "y": y})

    while True:
        await asyncio.sleep(1)

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())

import asyncio
from playwright.async_api import async_playwright, Playwright

from access import access


async def run(playwright: Playwright):
    canvas = await access(playwright)

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
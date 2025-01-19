from playwright.sync_api import sync_playwright, Playwright
from login import login
from click import click


def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    page = browser.new_page()

    login(page)

    page.wait_for_timeout(15000)
    canvas = (
        page.locator('iframe[name="game_frame"]')
        .content_frame.locator("#htmlWrap")
        .content_frame.locator("canvas")
    )

    click(canvas, x_range=(700, 1100), y_range=(560, 640))

    page.wait_for_timeout(100000)
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

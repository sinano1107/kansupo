from playwright.async_api import Playwright


async def access(playwright: Playwright):
    chromium = playwright.chromium
    browser = await chromium.launch(headless=False)
    context = await browser.new_context(storage_state="login_account.json")
    page = await context.new_page()
    page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
    
    canvas = (
        page.locator('iframe[name="game_frame"]')
            .content_frame.locator("#htmlWrap")
            .content_frame.locator("canvas")
    )
    
    return canvas
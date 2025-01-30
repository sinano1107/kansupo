import asyncio
import json
import os
from playwright.async_api import async_playwright, Response
from datetime import datetime

# ゲームプレイ中のレスポンスをtxtファイルとして記録する

API_ROOT_PATH = "http://w14h.kancolle-server.com/kcsapi/"
async def record_response(res: Response, start_date: datetime):
    if not res.url.startswith(API_ROOT_PATH):
        return
    
    api_name = res.url[len(API_ROOT_PATH):]
    text = await res.text()
    data = json.loads(text[7:])
    
    if not os.path.isdir(f"responses/{start_date}"):
        os.makedirs(f"responses/{start_date}")
    
    with open(f"responses/{start_date}/{datetime.now()}_{api_name.replace("/", "-")}.txt", "w") as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))
        print(api_name + "のレスポンスを記録しました")

async def main():
    async with async_playwright() as p:
        start_date = datetime.now()
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="login_account.json")
        p_page = await context.new_page()
        p_page.on("response", lambda res: record_response(res, start_date))
        await p_page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
        
        while True:
            await asyncio.sleep(1)
    
    while True:
        for i in range(4):
            print("\rwaiting" + "." * i + " " * (3 - i), end="")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
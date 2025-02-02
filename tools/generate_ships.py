import asyncio
import json
from playwright.async_api import async_playwright, Response

from ndock_only_async import click, random_sleep, wait_until_find
from scan.targets.targets import GAME_START_SCAN_TARGET

should_finish = False

async def handle_response(res: Response):
    if res.url != "http://w14h.kancolle-server.com/kcsapi/api_start2/getData":
        return
    
    global should_finish
    data = json.loads((await res.body())[7:]).get("api_data")
    
    ship_list = data.get("api_mst_ship")
    
    # 駆逐艦イ級以前に味方艦の情報が格納されているので、それのインデックスを取得する
    end_index = None
    # 開発時点でのイ級のインデックス以降を探索する
    for i in range(792, len(ship_list)):
        if ship_list[i].get("api_id") == 1501:
            end_index = i
            break
    ship_list = ship_list[:end_index]
    
    ships_str = ""
    dict_str = ""
    
    for ship in ship_list:
        id = ship.get("api_id")
        name = ship.get("api_name")
        replaced_name = name.replace(" ", "_").replace("-", "_").replace(".", "_")
        fuel_max = ship.get("api_fuel_max")
        bull_max = ship.get("api_bull_max")
        ships_str += f"{replaced_name} = Ship({id=}, {name=}, {fuel_max=}, {bull_max=})\n"
        dict_str += f"\t{id}: {replaced_name},\n"
    
    with open("ships/ships.py", "w") as f:
        f.write(f"from .ship import Ship\n\n\n{ships_str}\n\nships_map = {{\n{dict_str}}}")
    
    should_finish = True

async def main():
    async with async_playwright() as p:
        global canvas, sortie
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="login_account.json", viewport={"width": 1300, "height": 900})
        page = await context.new_page()
        page.on("response", handle_response)
        await page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
        canvas = (
            page.locator('iframe[name="game_frame"]')
                .content_frame.locator("#htmlWrap")
                .content_frame.locator("canvas")
        )
        
        await wait_until_find(canvas, GAME_START_SCAN_TARGET)
        await random_sleep()
        await click(canvas, GAME_START_SCAN_TARGET.RECTANGLE)
        
        while not should_finish:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
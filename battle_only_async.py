import asyncio
from datetime import datetime
import json
from typing import Coroutine
from playwright.async_api import async_playwright, Response, Locator

from ndock_only_async import Page, click, random_sleep, scan, wait_until_find
from record_response import record_response
from scan_targets.index import SEA_AREA_SELECT_SCAN_TARGET, SETTING_SCAN_TARGET, SORTIE_SELECT_SCAN_TARGET, SORTIE_NEXT_SCAN_TARGET, GO_BACK_SCAN_TARGET, WITHDRAWAL_SCAN_TARGET
from targets import GAME_START, SEA_AREA_LEFT_TOP, SEA_AREA_SELECT_DECIDE, SORTIE, SORTIE_START, SELECT_SINGLE_LINE, SUPPLY, ATTACK
from scan_targets.index import COMPASS, TAN


page: Page = Page.START
canvas: Locator = None
sortie: Coroutine = None
response: dict = None

def calc_remaining_hp():
    """
    味方・敵 艦隊の残りHPを計算する
    """
    hourai_flag = response.get("api_hourai_flag")
    friend_now_hp_list = response.get("api_f_nowhps")
    enemy_now_hp_list = response.get("api_e_nowhps")
    total_friend_damage_list = [0] * 6
    total_enemy_damage_list = [0] * 6
    
    if response.get("api_openeing_taisen_flag") == 1:
        # TODO 先制対潜のダメージを計算する
        print("🚨先制対潜のダメージ計算は実装されていないです")
    else:
        print("<先制対潜は発生しませんでした>")
    
    if response.get("api_opening_flag") == 1:
        # TODO 先制雷撃のダメージを計算する
        print("🚨先制雷撃のダメージ計算は実装されていないです")
    else:
        print("先制雷撃は発生しませんでした")
    
    # 砲撃戦の情報を取得する
    for i in range(3):
        flag = hourai_flag[i]
        if flag == 0:
            break
        
        print("<砲撃戦" + str(i+1) + "巡目>")
        
        hougeki_data = response.get(f"api_hougeki{i+1}")
        # 行動陣営フラグ 0=味方, 1=敵
        at_e_flag_list = hougeki_data.get("api_at_eflag")
        df_list = hougeki_data.get("api_df_list")
        damage_list = hougeki_data.get("api_damage")
        for i, at_e_flag in enumerate(at_e_flag_list):
            index = df_list[i][0]
            damage = damage_list[i][0]
            
            # 庇った場合はdamage+0.1になるのでそれを処理する
            is_protected = damage % 1 == 0.1
            damage //= 1
            
            # ダメージを記録
            if at_e_flag == 1:
                print(f"味方の{index + 1}隻目に{damage}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
                total_friend_damage_list[index] += damage
            else:
                print(f"敵の{index + 1}隻目に{damage}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
                total_enemy_damage_list[index] += damage
    
    # 雷撃戦の情報を取得する
    if hourai_flag[3] == 1:
        raigeki = response.get("api_raigeki")
        fdam = raigeki.get("api_fdam")
        edam = raigeki.get("api_edam")
        
        for i, f in enumerate(fdam[:6]):
            print(f"味方の{i+1}隻目に{f}ダメージ")
            total_friend_damage_list[i] += f

        for i, e in enumerate(edam[:6]):
            print(f"敵の{i+1}隻目に{e}ダメージ")
            total_enemy_damage_list[i] += e
    else:
        print("<雷撃戦は発生しませんでした>")
    
    friend_remaining_hp_list = [now - damage for now, damage in zip(friend_now_hp_list, total_friend_damage_list)]
    enemy_remaining_hp_list = [now - damage for now, damage in zip(enemy_now_hp_list, total_enemy_damage_list)]
    
    print("<トータルダメージ>")
    print(f"味方の被ダメージ合計: {total_friend_damage_list}")
    print(f"敵の被ダメージ合計: {total_enemy_damage_list}")
    print("<残りHP>")
    print(f"味方の残りHP: {friend_remaining_hp_list}")
    print(f"敵の残りHP: {enemy_remaining_hp_list}")
    
    return (friend_remaining_hp_list, enemy_remaining_hp_list)

async def sortie_1_1():
    await asyncio.to_thread(input, "<補給済みですか？Enterで出撃します>")
    
    print("1-1に出撃します")
    
    print("出撃ボタンを押下します")
    await click(canvas, SORTIE)
    
    print("出撃画面が出現するまで待機します")
    await wait_until_find(canvas, SORTIE_SELECT_SCAN_TARGET)
    print("出撃画面が出現しました")
    
    await random_sleep()
    
    print("出撃を選択します")
    await click(canvas, SORTIE_SELECT_SCAN_TARGET.RECTANGLE)
    
    print("海域選択画面が出現するまで待機します")
    await wait_until_find(canvas, SEA_AREA_SELECT_SCAN_TARGET)
    print("海域選択画面が出現しました")
    
    await random_sleep()
    
    print("左上の海域を選択します")
    await click(canvas, SEA_AREA_LEFT_TOP)

    await random_sleep()

    print("決定します")
    await click(canvas, SEA_AREA_SELECT_DECIDE)
    print("決定しました")
    
    await random_sleep()
    
    print("出撃開始ボタンを押下します")
    await click(canvas, SORTIE_START)
    
    print("出撃を開始するまで待機します")
    while page != Page.SORTIE_START:
        await asyncio.sleep(1)
    print("出撃を開始しました")
    
    # これ以降はおそらくループで処理することで一般化できる
    
    while True:
        # 次のセルから派生しているセルの個数
        next = response.get("api_next")
        
        # 次がボスマスかどうか確認する
        # is_next_boss = response.get("api_event_id") == 5
        
        # 羅針盤が表示されるか確認する
        rashin_flag = response.get("api_rashin_flg")
        if rashin_flag == 1:
            print("羅針盤が表示されるまで待機します")
            await wait_until_find(canvas, COMPASS)
            print("羅針盤が表示されました")
            await random_sleep()
            print("画面をクリックします")
            await click(canvas)
            print("画面をクリックしました")
            await random_sleep()
        else:
            print("羅針盤は表示されません")
        
        print("単縦陣選択画面が表示されるまで待機します")
        await wait_until_find(canvas, TAN)
        print("単縦陣選択ボタンが表示されました")
        await random_sleep()
        
        print("単縦陣選択ボタンをクリックします")
        await click(canvas, SELECT_SINGLE_LINE)
        print("単縦陣を選択しました")
        
        print("戦闘開始まで待機します")
        while page != Page.BATTLE:
            await asyncio.sleep(1)
        print("戦闘が開始されました")
        
        friend_remaining_hp_list, enemy_remaining_hp_list = calc_remaining_hp()
        
        can_midnight_battle = any(hp > 0 for hp in enemy_remaining_hp_list)
        if can_midnight_battle:
            print("夜戦を行えます<未実装>")
            return
            # if is_next_boss:
            #     print("ボスマスなので夜戦を行います")
            # else:
            #     print("ボスマスではないので、夜戦を行いません")
            
            # print("夜戦選択画面が表示されるまで待機します")
            # await wait_until_find(canvas, )
        else:
            print("敵を倒し切ったので夜戦を行うことができません")
        
        huge_damage_list = [remaining_hp <= max // 4 for remaining_hp, max in zip(friend_remaining_hp_list, response.get("api_f_maxhps"))]
        
        print("戦闘終了まで待機します")
        while page != Page.BATTLE_RESULT:
            await asyncio.sleep(1)
        print("戦闘終了しました")
        
        print("次へボタンが表示されるまで待機します(1)")
        await wait_until_find(canvas, SORTIE_NEXT_SCAN_TARGET)
        print("次へボタンが表示されました(1)")
        
        await random_sleep(2)
        
        print("次へ進みます(1)")
        await click(canvas)
        print("次へ進みました(1)")
        
        await random_sleep()
        
        print("次へボタンが表示されるまで待機します(2)")
        await wait_until_find(canvas, SORTIE_NEXT_SCAN_TARGET)
        print("次へボタンが表示されました(2)")
        
        await random_sleep()
        
        print("次へ進みます(2)")
        await click(canvas)
        print("次へ進みました(2)")
        
        await random_sleep()
        
        get_flag = response.get("api_get_flag")
        if get_flag[1] == 1:
            get_ship = response.get("api_get_ship")
            print(f"艦娘を取得しました: {get_ship.get('api_ship_name')}")
            print("帰るボタンが表示されるまで待機します")
            await wait_until_find(canvas, GO_BACK_SCAN_TARGET)
            await random_sleep()
            print("画面をクリックします")
            await click(canvas)
        
        if next == 0:
            print("行き止まりなので終了")
            return
        
        print("撤退ボタンが表示されるまで待機します")
        await wait_until_find(canvas, WITHDRAWAL_SCAN_TARGET)
        print("撤退ボタンが表示されました")
        
        await random_sleep()
        
        if any(huge_damage_list):
            print("大破艦がいるので撤退します")
            await click(canvas, WITHDRAWAL_SCAN_TARGET.RECTANGLE)
            return
        
        print("進撃ボタンをクリックします")
        await click(canvas, ATTACK)
        
        print("次のセルへ向かうレスポンスが帰ってくるまで待機します")
        while page != Page.GOING_TO_NEXT_CELL:
            await asyncio.sleep(1)
        print("次のセルへ向かうレスポンスが帰ってきました")


async def handle_response(res: Response):
    if not res.url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return
    
    global page, response, sortie
    url = res.url
    
    if url.endswith("/api_port/port"):
        print("母港に到達しました")
        page = Page.PORT
        
        if sortie is not None:
            print("出撃コルーチンが代入されているので、処理を終了します")
            return
        
        svdata: dict = json.loads((await res.body())[7:])
        data: dict = svdata.get("api_data")
        
        # 所持艦船リスト
        ship_list = data.get("api_ship")
        # 所持艦船のID: 受けているダメージの辞書
        ship_damage_map = {ship.get("api_id"): ship.get("api_maxhp") - ship.get("api_nowhp") for ship in ship_list}
        
        # 現在編成中の艦隊
        deck_port = data.get("api_deck_port")
        
        # 第一艦隊の損害を確認
        for ship_id in deck_port[0].get("api_ship"):
            if ship_id == -1:
                # 飛ばし飛ばしで編成することはできないので、からのスロットがあり次第ループを離脱
                break
        
            if ship_damage_map[ship_id] > 0:
                print("第一艦隊に損傷艦が含まれています\n編成を行なってください")
                return
        
        # 第一艦隊に損害がないので、出撃する
        print("第一艦隊に損害がないので、出撃コルーチンを代入します")
        sortie = sortie_1_1
    elif url.endswith("api_req_map/start"):
        print("出撃開始レスポンスを受け取りました")
        response = json.loads((await res.body())[7:]).get("api_data")
        page = Page.SORTIE_START
    elif url.endswith("/api_req_sortie/battle"):
        print("戦闘開始レスポンスを受け取りました")
        response = json.loads((await res.body())[7:]).get("api_data")
        page = Page.BATTLE
    elif url.endswith("/api_req_sortie/battleresult"):
        print("戦闘結果レスポンスを受け取りました")
        response = json.loads((await res.body())[7:]).get("api_data")
        page = Page.BATTLE_RESULT
    elif url.endswith("/api_req_map/next"):
        print("次のセルへ向かうレスポンスを受け取りました")
        response = json.loads((await res.body())[7:]).get("api_data")
        page = Page.GOING_TO_NEXT_CELL
    else:
        print("ハンドラの設定されていないレスポンスを受け取りました")

async def main():
    name = "battle_only_async_test"
    name += datetime.now().strftime("_%Y%m%d_%H%M%S")
    async with async_playwright() as p:
        global canvas, sortie
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="login_account.json", record_video_dir=f"responses/{name}", viewport={"width": 1300, "height": 900})
        p_page = await context.new_page()
        p_page.on("response", handle_response)
        p_page.on("response", lambda res: record_response(res, name))
        await p_page.goto("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854")
        canvas = (
            p_page.locator('iframe[name="game_frame"]')
                .content_frame.locator("#htmlWrap")
                .content_frame.locator("canvas")
        )
        
        await random_sleep(5, 3)
        # スタートページにいる限り、ゲームスタートボタンの位置を定期的にクリックする
        while page == Page.START:
            await click(canvas, GAME_START)
            await random_sleep()
        
        # 右下に設定ボタンが出現するまで待機する
        while True:
            if await scan(canvas, [SETTING_SCAN_TARGET]) == 0:
                break
            await asyncio.sleep(1)
        
        print("ゲームスタート処理を終了しました")
        await random_sleep()
        
        while True:
            for i in range(4):
                if sortie is None:
                    # コルーチンが空の場合は待機
                    print("\rwaiting" + "." * i + " " * (3 - i), end="")
                else:
                    # コルーチンが空でない場合は処理を実行
                    print("\rprocess start!")
                    await sortie()
                    sortie = None
                # 1秒ごとに確認
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
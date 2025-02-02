import asyncio
import json
from typing import Coroutine
from playwright.async_api import async_playwright, Response, Locator

from scan.targets.targets import SEA_AREA_SELECT_SCAN_TARGET, SORTIE_SELECT_SCAN_TARGET, SORTIE_NEXT_SCAN_TARGET, GO_BACK_SCAN_TARGET, WITHDRAWAL_SCAN_TARGET, MIDNIGHT_BATTLE_SELECT_PAGE
from targets.targets import SEA_AREA_LEFT_TOP, SEA_AREA_SELECT_DECIDE, SORTIE, SORTIE_START, SELECT_SINGLE_LINE, ATTACK, DO_MIDNIGHT_BATTLE, NO_MIDNIGHT_BATTLE
from scan.targets.targets import COMPASS, TAN
from ships.ships import ships_map
from utils.game_start import game_start
from utils.wait_until_find import wait_until_find
from utils.click import click
from utils.random_sleep import random_sleep
from utils.page import Page


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
            for index, damage in zip(df_list[i], damage_list[i]):
                # 庇った場合はdamage+0.1になるのでそれを処理する
                damage, mod = divmod(damage, 1)
                is_protected = mod != 0
                
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
            # 庇った場合はdamage+0.1になるのでそれを処理する
            damage, mod = divmod(damage, 1)
            is_protected = mod != 0
            print(f"味方の{i+1}隻目に{f}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
            total_friend_damage_list[i] += f

        for i, e in enumerate(edam[:6]):
            # 庇った場合はdamage+0.1になるのでそれを処理する
            damage, mod = divmod(damage, 1)
            is_protected = mod != 0
            print(f"敵の{i+1}隻目に{e}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
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
    await random_sleep()
    
    print("1-1に出撃します")
    
    await click(canvas, SORTIE)
    
    print("出撃画面が出現するまで待機します")
    await wait_until_find(canvas, SORTIE_SELECT_SCAN_TARGET)
    print("出撃画面が出現しました")
    
    await random_sleep()
    
    await click(canvas, SORTIE_SELECT_SCAN_TARGET.RECTANGLE)
    
    print("海域選択画面が出現するまで待機します")
    await wait_until_find(canvas, SEA_AREA_SELECT_SCAN_TARGET)
    print("海域選択画面が出現しました")
    
    await random_sleep()
    
    await click(canvas, SEA_AREA_LEFT_TOP)

    await random_sleep()

    await click(canvas, SEA_AREA_SELECT_DECIDE)
    
    await random_sleep()
    
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
        is_next_boss = response.get("api_event_id") == 5
        
        # 羅針盤が表示されるか確認する
        rashin_flag = response.get("api_rashin_flg")
        if rashin_flag == 1:
            print("羅針盤が表示されるまで待機します")
            await wait_until_find(canvas, COMPASS)
            print("羅針盤が表示されました")
            await random_sleep()
            await click(canvas)
            await random_sleep()
        else:
            print("羅針盤は表示されません")
        
        event_id = response.get("api_event_id")
        
        # 「気のせいだった」の時はスキップする
        if event_id == 6:
            continue
        
        # FIXME 4隻未満のとき、陣形選択ができないので、この処理をスキップする
        print("単縦陣選択画面が表示されるまで待機します")
        await wait_until_find(canvas, TAN)
        print("単縦陣選択ボタンが表示されました")
        await random_sleep()
        await click(canvas, SELECT_SINGLE_LINE)
        
        print("戦闘開始まで待機します")
        while page != Page.BATTLE:
            await asyncio.sleep(1)
        print("戦闘が開始されました")
        
        friend_remaining_hp_list, enemy_remaining_hp_list = calc_remaining_hp()
        
        can_midnight_battle = any(hp > 0 for hp in enemy_remaining_hp_list)
        if can_midnight_battle:
            print("夜戦選択画面が表示されるまで待機します")
            await wait_until_find(canvas, MIDNIGHT_BATTLE_SELECT_PAGE)
            print("夜戦選択画面が表示されました")
            
            await random_sleep()
            
            if is_next_boss:
                print("ボスマスなので夜戦を行います")
                await click(canvas, DO_MIDNIGHT_BATTLE)
                
                print("夜戦開始まで待機します")
                while page != Page.MIDNIGHT_BATTLE:
                    await asyncio.sleep(1)
                print("夜戦が開始されました")
                
                hougeki = response.get("api_hougeki")
                at_e_flag_list = hougeki.get("api_at_eflag")
                
                if at_e_flag_list is None:
                    print("夜戦が発生しませんでした")
                else:
                    now_hp_list = response.get("api_f_nowhps")
                    df_list = hougeki.get("api_df_list")
                    damage_list = hougeki.get("api_damage")
                    total_friend_damage_list = [0] * 6
                    
                    for i, at_e_flag in enumerate(at_e_flag_list):
                        if at_e_flag == 1:
                            for index, damage in zip(df_list[i], damage_list[i]):
                                # 庇った場合はdamage+0.1になるのでそれを処理する
                                is_protected = damage % 1 == 0.1
                                damage //= 1
                                
                                print(f"味方の{index+1}隻目に{damage}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
                                total_friend_damage_list[index] += damage
                    
                    friend_remaining_hp_list = [now - damage for now, damage in zip(now_hp_list, total_friend_damage_list)]
            else:
                print("ボスマスではないので、夜戦を行いません")
                await click(canvas, NO_MIDNIGHT_BATTLE)
        else:
            print("敵を倒し切ったので夜戦を行うことができません")
        
        huge_damage_list = [remaining_hp <= max // 4 for remaining_hp, max in zip(friend_remaining_hp_list, response.get("api_f_maxhps"))]
        
        print("戦闘終了画面に遷移するまで待機します")
        while page != Page.BATTLE_RESULT:
            await asyncio.sleep(1)
        print("戦闘終了画面に遷移しました")
        
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
        # 所持艦船のID: 受けているダメージ、所持燃料数/弾薬数の辞書
        ship_data_map = {
            ship.get("api_id"):  {
                "ship_id": ship.get("api_ship_id"),
                "damage": ship.get("api_maxhp") - ship.get("api_nowhp"),
                "fuel": ship.get("api_fuel"),
                "bull": ship.get("api_bull"),
            }
        for ship in ship_list}
        
        # 現在編成中の艦隊
        deck_port = data.get("api_deck_port")
        
        # 第一艦隊の損害/補給状況を確認
        for ship_id in deck_port[0].get("api_ship"):
            if ship_id == -1:
                # 飛ばし飛ばしで編成することはできないので、からのスロットがあり次第ループを離脱
                break
            
            ship_data = ship_data_map.get(ship_id)
        
            # 損害を確認
            if ship_data.get("damage") > 0:
                print("第一艦隊に損傷艦が含まれています\n編成を行なってください")
                return
            
            mst_ship_data = ships_map.get(ship_data.get("ship_id"))
            if mst_ship_data is None:
                print(f"艦の情報が取得できませんでした {ship_id=}")
                return
            
            # 補給状況を確認
            if mst_ship_data.fuel_max > ship_data.get("fuel") or mst_ship_data.bull_max > ship_data.get("bull"):
                print("第一艦隊の補給が必要です")
                return
        
        # 第一艦隊に損害がないので、出撃する
        print("第一艦隊の出撃に支障がないので、出撃コルーチンを代入します")
        sortie = sortie_1_1
    elif url.endswith("api_req_map/start"):
        print("出撃開始レスポンスを受け取りました")
        response = json.loads((await res.body())[7:]).get("api_data")
        page = Page.SORTIE_START
    elif url.endswith("/api_req_sortie/battle"):
        print("戦闘開始レスポンスを受け取りました")
        response = json.loads((await res.body())[7:]).get("api_data")
        page = Page.BATTLE
    elif url.endswith("/api_req_battle_midnight/battle"):
        print("夜戦開始レスポンスを受け取りました")
        response = json.loads((await res.body())[7:]).get("api_data")
        page = Page.MIDNIGHT_BATTLE
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
    async with async_playwright() as p:
        global canvas, sortie
        canvas = await game_start(p, handle_response)
        
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
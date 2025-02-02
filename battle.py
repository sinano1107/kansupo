import asyncio
from playwright.async_api import async_playwright, Response

from scan.targets.targets import SEA_AREA_SELECT_SCAN_TARGET, SORTIE_SELECT_SCAN_TARGET, SORTIE_NEXT_SCAN_TARGET, GO_BACK_SCAN_TARGET, WITHDRAWAL_SCAN_TARGET, MIDNIGHT_BATTLE_SELECT_PAGE
from targets.targets import SEA_AREA_LEFT_TOP, SEA_AREA_SELECT_DECIDE, SORTIE, SORTIE_START, SELECT_SINGLE_LINE, ATTACK, DO_MIDNIGHT_BATTLE, NO_MIDNIGHT_BATTLE
from scan.targets.targets import COMPASS, TAN
from ships.ships import ships_map
from utils.game_start import game_start
from utils.wait_until_find import wait_until_find
from utils.click import click
from utils.random_sleep import random_sleep
from utils.page import Page
from utils.context import BattleResponse, Context, ResponseMemory


def calc_remaining_hp():
    """
    味方・敵 艦隊の残りHPを計算する
    """
    response = ResponseMemory.battle
    total_friend_damage_list = [0] * 6
    total_enemy_damage_list = [0] * 6
    
    if response.opening_taisen_flag:
        # TODO 先制対潜のダメージを計算する
        print("🚨先制対潜のダメージ計算は実装されていないです")
    else:
        print("<先制対潜は発生しませんでした>")
    
    if response.opening_flag:
        # TODO 先制雷撃のダメージを計算する
        print("🚨先制雷撃のダメージ計算は実装されていないです")
    else:
        print("先制雷撃は発生しませんでした")
    
    # 砲撃戦の情報を取得する
    for i in range(3):
        flag = response.hourai_flag[i]
        if not flag:
            break
        
        print("<砲撃戦" + str(i+1) + "巡目>")
        
        hougeki_data: BattleResponse.Hougeki = getattr(response, f"hougeki{i+1}")

        for i, at_eflag in enumerate(hougeki_data.at_eflag_list):
            for index, damage in zip(hougeki_data.df_list[i], hougeki_data.damage_list[i]):
                # 庇った場合はdamage+0.1になるのでそれを処理する
                damage, mod = divmod(damage, 1)
                is_protected = mod != 0
                
                # ダメージを記録
                if at_eflag == 1:
                    print(f"味方の{index + 1}隻目に{damage}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
                    total_friend_damage_list[index] += damage
                else:
                    print(f"敵の{index + 1}隻目に{damage}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
                    total_enemy_damage_list[index] += damage
    
    # 雷撃戦の情報を取得する
    if response.hourai_flag[3]:
        raigeki = response.raigeki
        
        for i, damage in enumerate(raigeki.fdam[:6]):
            # 庇った場合はdamage+0.1になるのでそれを処理する
            damage, mod = divmod(damage, 1)
            is_protected = mod != 0
            print(f"味方の{i+1}隻目に{damage}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
            total_friend_damage_list[i] += damage

        for i, damage in enumerate(raigeki.edam[:6]):
            # 庇った場合はdamage+0.1になるのでそれを処理する
            damage, mod = divmod(damage, 1)
            is_protected = mod != 0
            print(f"敵の{i+1}隻目に{damage}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
            total_enemy_damage_list[i] += damage
    else:
        print("<雷撃戦は発生しませんでした>")
    
    friend_remaining_hp_list = [now - damage for now, damage in zip(response.friend_now_hp_list, total_friend_damage_list)]
    enemy_remaining_hp_list = [now - damage for now, damage in zip(response.enemy_now_hp_list, total_enemy_damage_list)]
    
    print("<トータルダメージ>")
    print(f"味方の被ダメージ合計: {total_friend_damage_list}")
    print(f"敵の被ダメージ合計: {total_enemy_damage_list}")
    print("<残りHP>")
    print(f"味方の残りHP: {friend_remaining_hp_list}")
    print(f"敵の残りHP: {enemy_remaining_hp_list}")
    
    return (friend_remaining_hp_list, enemy_remaining_hp_list)

async def sortie_1_1():
    print("1-1に出撃します")
    await random_sleep()
    
    await click(SORTIE)
    await wait_until_find(SORTIE_SELECT_SCAN_TARGET)
    await random_sleep()
    
    await click(SORTIE_SELECT_SCAN_TARGET.RECTANGLE)
    await wait_until_find(SEA_AREA_SELECT_SCAN_TARGET)
    await random_sleep()
    
    await click(SEA_AREA_LEFT_TOP)
    await random_sleep()
    
    await click(SEA_AREA_SELECT_DECIDE)
    await random_sleep()
    
    await click(SORTIE_START)
    
    print("出撃を開始するまで待機します")
    while Context.page != Page.SORTIE_START:
        await asyncio.sleep(1)
    print("出撃を開始しました")
    
    while True:
        map_next_response = ResponseMemory.map_next
        
        # 羅針盤が表示されるか確認する
        if map_next_response.rashin_flag:
            await wait_until_find(COMPASS)
            await random_sleep()
            await click()
            await random_sleep()
        else:
            print("羅針盤は表示されません")
        
        # 「気のせいだった」の時はスキップする
        if map_next_response.event_id == 6:
            continue
        
        # FIXME 4隻未満のとき、陣形選択ができないので、この処理をスキップする
        await wait_until_find(TAN)
        await random_sleep()
        await click(SELECT_SINGLE_LINE)
        
        print("戦闘開始まで待機します")
        while Context.page != Page.BATTLE:
            await asyncio.sleep(1)
        print("戦闘が開始されました")
        
        friend_remaining_hp_list, enemy_remaining_hp_list = calc_remaining_hp()
        friend_max_hp_list = ResponseMemory.battle.friend_max_hp_list
        
        can_midnight_battle = any(hp > 0 for hp in enemy_remaining_hp_list)
        if can_midnight_battle:
            await wait_until_find(MIDNIGHT_BATTLE_SELECT_PAGE)
            
            await random_sleep()
            
            if map_next_response.event_id == 5:
                print("ボスマスなので夜戦を行います")
                await click(DO_MIDNIGHT_BATTLE)
                
                print("夜戦開始まで待機します")
                while Context.page != Page.MIDNIGHT_BATTLE:
                    await asyncio.sleep(1)
                print("夜戦が開始されました")
                
                midnight_battle_response = ResponseMemory.midnight_battle
                
                hougeki = midnight_battle_response.hougeki
                
                if hougeki.at_eflag_list is None:
                    print("夜戦が発生しませんでした")
                else:
                    total_friend_damage_list = [0] * 6
                    
                    for i, at_e_flag in enumerate(hougeki.at_eflag_list):
                        if at_e_flag == 1:
                            for index, damage in zip(hougeki.df_list[i], hougeki.damage_list[i]):
                                # 庇った場合はdamage+0.1になるのでそれを処理する
                                is_protected = damage % 1 == 0.1
                                damage //= 1
                                
                                print(f"味方の{index+1}隻目に{damage}ダメージ{"(旗艦を庇った)" if is_protected else ""}")
                                total_friend_damage_list[index] += damage
                    
                    friend_remaining_hp_list = [now - damage for now, damage in zip(midnight_battle_response.friend_now_hp_list, total_friend_damage_list)]
                    friend_max_hp_list = midnight_battle_response.friend_max_hp_list
            else:
                print("ボスマスではないので、夜戦を行いません")
                await click(NO_MIDNIGHT_BATTLE)
        else:
            print("敵を倒し切ったので夜戦を行うことができません")
        
        huge_damage_list = [remaining_hp <= max // 4 for remaining_hp, max in zip(friend_remaining_hp_list, friend_max_hp_list)]
        
        print("戦闘終了画面に遷移するまで待機します")
        while Context.page != Page.BATTLE_RESULT:
            await asyncio.sleep(1)
        print("戦闘終了画面に遷移しました")
        
        await wait_until_find(SORTIE_NEXT_SCAN_TARGET)
        await random_sleep(2)
        
        await click()
        await random_sleep()
        
        await wait_until_find(SORTIE_NEXT_SCAN_TARGET)
        await random_sleep()
        
        await click()
        await random_sleep()
        
        battle_result_response = ResponseMemory.battle_result
        if battle_result_response.get_flag[1]:
            print(f"艦娘を取得しました: {battle_result_response.get_ship.name}")
            await wait_until_find(GO_BACK_SCAN_TARGET)
            await random_sleep()
            await click()
        
        if map_next_response.next == 0:
            print("行き止まりなので終了")
            return
        
        await wait_until_find(WITHDRAWAL_SCAN_TARGET)
        
        await random_sleep()
        
        if any(huge_damage_list):
            print("大破艦がいるので撤退します")
            await click(WITHDRAWAL_SCAN_TARGET.RECTANGLE)
            return
        
        await click(ATTACK)
        
        print("次のセルへ向かうレスポンスが帰ってくるまで待機します")
        while Context.page != Page.GOING_TO_NEXT_CELL:
            await asyncio.sleep(1)
        print("次のセルへ向かうレスポンスが帰ってきました")


async def handle_response(res: Response):
    if not res.url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return

    url = res.url
    
    if url.endswith("/api_port/port"):
        print("母港に到達しました")
        Context.set_page(Page.PORT)
        await Context.set_page_and_response(Page.PORT, res)
        
        if Context.task is not None:
            print("コルーチンが代入されているので、処理を終了します")
            return
        
        await ResponseMemory.set_response(Page.PORT, res)
        port_response = ResponseMemory.port
        
        # 第一艦隊の損害/補給状況を確認
        for ship_id in port_response.deck_port[0].ship_id_list:
            if ship_id == -1:
                # 飛ばし飛ばしで編成することはできないので、からのスロットがあり次第ループを離脱
                break
            
            # 編成中の艦の情報を取得
            for ship in port_response.ship_list:
                if ship.id == ship_id:
                    ship_data = ship
                    break
        
            # 損害を確認
            if ship_data.damage > 0:
                print("第一艦隊に損傷艦が含まれています\n編成を行なってください")
                return
            
            mst_ship_data = ships_map.get(ship_data.ship_id)
            if mst_ship_data is None:
                print(f"艦の情報が取得できませんでした {ship_id=}")
                return
            
            # 補給状況を確認
            if mst_ship_data.fuel_max > ship_data.fuel or mst_ship_data.bull_max > ship_data.bull:
                print("第一艦隊の補給が必要です")
                return
        
        # 第一艦隊に損害がないので、出撃する
        print("第一艦隊の出撃に支障がないので、出撃コルーチンを代入します")
        Context.set_task(sortie_1_1)
    elif url.endswith("api_req_map/start"):
        print("出撃開始レスポンスを受け取りました")
        await Context.set_page_and_response(Page.SORTIE_START, res)
    elif url.endswith("/api_req_sortie/battle"):
        print("戦闘開始レスポンスを受け取りました")
        await Context.set_page_and_response(Page.BATTLE, res)
    elif url.endswith("/api_req_battle_midnight/battle"):
        print("夜戦開始レスポンスを受け取りました")
        await Context.set_page_and_response(Page.MIDNIGHT_BATTLE, res)
    elif url.endswith("/api_req_sortie/battleresult"):
        print("戦闘結果レスポンスを受け取りました")
        await Context.set_page_and_response(Page.BATTLE_RESULT, res)
    elif url.endswith("/api_req_map/next"):
        print("次のセルへ向かうレスポンスを受け取りました")
        await Context.set_page_and_response(Page.GOING_TO_NEXT_CELL, res)
    else:
        print("ハンドラの設定されていないレスポンスを受け取りました")

async def main():
    async with async_playwright() as p:
        await game_start(p, handle_response)
        
        while True:
            for i in range(4):
                if Context.task is None:
                    # コルーチンが空の場合は待機
                    print("\rwaiting" + "." * i + " " * (3 - i), end="")
                else:
                    # コルーチンが空でない場合は処理を実行
                    print("\rprocess start!")
                    await Context.do_task()
                # 1秒ごとに確認
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
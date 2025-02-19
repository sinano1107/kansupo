import asyncio
import math
from playwright.async_api import async_playwright, Response

from clean import calc_resource_ships
from expedition import handle_expedition_returned
from scan.targets.targets import (
    FORMATION_SELECT_SCAN_TARGET,
    HOME_PORT_SCAN_TARGET,
    SEA_AREA_SELECT_SCAN_TARGET,
    SETTING_SCAN_TARGET,
    SORTIE_SELECT_PAGE_SCAN_TARGET,
    SORTIE_NEXT_SCAN_TARGET,
    GO_BACK_SCAN_TARGET,
    WITHDRAWAL_CIRCLE_SCAN_TARGET,
    WITHDRAWAL_SCAN_TARGET,
    MIDNIGHT_BATTLE_SELECT_PAGE,
)
from ships.ndock_rate import ndock_rate
from ships.ship import SType
from targets.targets import (
    HOME_PORT,
    ORGANIZATION,
    RELEASE_ESCORT,
    SEA_AREA_SELECT_DECIDE,
    SHIP_CHANGE,
    SORTIE,
    SORTIE_SELECT,
    SORTIE_START,
    SELECT_SINGLE_LINE,
    ATTACK,
    DO_MIDNIGHT_BATTLE,
    NO_MIDNIGHT_BATTLE,
    change_ship_button,
    organization_page_from_the_left,
    organization_ship,
    sea_area,
)
from scan.targets.targets import COMPASS
from ships.ships import ships_map
from utils.calc_page_select_process import calc_page_select_process
from utils.game_start import game_start
from utils.wait_until_find import wait_until_find
from utils.click import click
from utils.random_sleep import random_sleep
from utils.page import Page
from utils.supply import supply
from utils.context import BattleResponse, Context, PortResponse, ResponseMemory


class SortieDestinationWrapper:
    maparea_id = 1
    mapinfo_no = 1


def calc_protected_damage(damage: int):
    """庇った場合はdamage+0.1になるのでそれを処理する"""
    damage, mod = divmod(damage, 1)
    is_protected = mod != 0
    return damage, is_protected


def calc_remaining_hp():
    """
    味方・敵 艦隊の残りHPを計算する
    """
    response = ResponseMemory.battle
    total_friend_damage_list = [0] * 6
    total_enemy_damage_list = [0] * 6

    if response.stage_flag[2]:
        print("<航空攻撃>")
        for i, damage in enumerate(response.kouku.stage3.fdam):
            damage, is_protected = calc_protected_damage(damage)
            print(
                f"味方の{i+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
            )
            total_friend_damage_list[i] += damage

        for i, damage in enumerate(response.kouku.stage3.edam):
            damage, is_protected = calc_protected_damage(damage)
            print(
                f"敵の{i+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
            )
            total_enemy_damage_list[i] += damage

    if response.opening_taisen_flag:
        # TODO 先制対潜のダメージを計算する
        print("🚨先制対潜のダメージ計算は実装されていないです")
    else:
        print("<先制対潜は発生しませんでした>")

    if response.opening_flag:
        # TODO 先制雷撃のダメージを計算する
        print("🚨先制雷撃のダメージ計算は実装されていないです")
    else:
        print("<先制雷撃は発生しませんでした>")

    # 砲撃戦の情報を取得する
    for i in range(3):
        flag = response.hourai_flag[i]
        if not flag:
            break

        print("<砲撃戦" + str(i+1) + "巡目>")

        hougeki_data: BattleResponse.Hougeki = getattr(response, f"hougeki{i+1}")

        for i, at_eflag in enumerate(hougeki_data.at_eflag_list):
            for index, damage in zip(hougeki_data.df_list[i], hougeki_data.damage_list[i]):
                damage, is_protected = calc_protected_damage(damage)

                # ダメージを記録
                if at_eflag == 1:
                    print(
                        f"味方の{index + 1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                    )
                    total_friend_damage_list[index] += damage
                else:
                    print(
                        f"敵の{index + 1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                    )
                    total_enemy_damage_list[index] += damage

    # 雷撃戦の情報を取得する
    if response.hourai_flag[3]:
        raigeki = response.raigeki

        for i, damage in enumerate(raigeki.fdam[:6]):
            damage, is_protected = calc_protected_damage(damage)
            print(
                f"味方の{i+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
            )
            total_friend_damage_list[i] += damage

        for i, damage in enumerate(raigeki.edam[:6]):
            damage, is_protected = calc_protected_damage(damage)
            print(
                f"敵の{i+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
            )
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


async def wait_until_going_next_cell():
    print("次のセルへ向かうレスポンスが帰ってくるまで待機します")
    while Context.page != Page.GOING_TO_NEXT_CELL:
        await asyncio.sleep(1)
    Context.page = None
    print("次のセルへ向かうレスポンスが帰ってきました")


async def sortie(fleet_size: int):
    maparea_id = SortieDestinationWrapper.maparea_id
    mapinfo_no = SortieDestinationWrapper.mapinfo_no

    print(f"{maparea_id}-{mapinfo_no}に出撃します")
    await random_sleep()

    await click(SORTIE)
    await wait_until_find(SORTIE_SELECT_PAGE_SCAN_TARGET)
    await random_sleep()

    await click(SORTIE_SELECT)
    await wait_until_find(SEA_AREA_SELECT_SCAN_TARGET)
    await random_sleep()

    await click(sea_area(maparea_id, mapinfo_no))
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

        event_id = map_next_response.event_id

        # イベントなし、資源獲得、渦潮、気のせいだった、の時はスキップする
        if event_id == 1 or event_id == 2 or event_id == 3 or event_id == 6:
            await wait_until_going_next_cell()
            continue

        # 戦闘、ボス戦以外の場合は対応していない
        if event_id != 4 and event_id != 5:
            print(
                "対応していないイベントが発生しました。スクリーンショットを撮影して終了します。"
            )
            await Context.canvas.screenshot(path="screenshot.png")
            exit()

        # FIXME 4隻未満のとき、陣形選択ができないので、この処理をスキップする
        if fleet_size >= 4:
            await wait_until_find(FORMATION_SELECT_SCAN_TARGET)
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

            if event_id == 5:
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
                                damage, is_protected = calc_protected_damage(damage)

                                print(
                                    f"味方の{index+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                                )
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

        if huge_damage_list[0]:
            print("旗艦が大破したので撤退します")
            await wait_until_find(WITHDRAWAL_CIRCLE_SCAN_TARGET)
            await random_sleep()
            await click()
            return

        await wait_until_find(WITHDRAWAL_SCAN_TARGET)

        await random_sleep()

        if any(huge_damage_list):
            print("大破艦がいるので撤退します")
            await click(WITHDRAWAL_SCAN_TARGET.RECTANGLE)
            return

        await click(ATTACK)

        await wait_until_going_next_cell()


def calc_fleet(resource_ships: list[PortResponse.Ship]) -> list[int]:
    """編成可能な艦隊を導出する"""

    # 1-3をターゲットとした編成を行う
    # 駆逐4自由2の編成を行う

    response = ResponseMemory.port
    other_fleet_ship_ids = response.other_fleet_ship_ids

    # まずは駆逐艦を揃える
    destroyer_candidate: list[PortResponse.Ship] = []
    free_backup_destroyer: list[PortResponse.Ship] = []
    for ship in response.ship_list:
        # 資源艦、他の艦隊に所属している、損傷を受けている、疲労がある、同じ艦を編成済みの場合は編成しない
        if (
            ship in resource_ships
            or ship.id in other_fleet_ship_ids
            or ship.damage > 0
            or ship.cond < 49
            or ship.ship_id
            in [s.ship_id for s in destroyer_candidate + free_backup_destroyer]
        ):
            continue

        # 駆逐艦ではない場合も編成しない
        if ship.stype != SType.Destroyer:
            continue

        # バックアップは駆逐艦が４隻揃ってから追加する
        if len(destroyer_candidate) < 4:
            destroyer_candidate.append(ship)
        else:
            free_backup_destroyer.append(ship)

        # 駆逐艦が4隻、自由編成バックアップ駆逐が2隻になったらループを抜ける
        if len(destroyer_candidate) == 4 and len(free_backup_destroyer) == 2:
            break

    if len(destroyer_candidate) != 4:
        # 編成不可能なのでNoneを返す
        return None

    # 次に自由編成艦を揃える
    free_candidate: list[PortResponse.Ship] = []
    free_backup_escorts: list[PortResponse.Ship] = []
    for ship in response.ship_list:
        # 駆逐艦はいらないので抜ける
        if ship.stype == SType.Destroyer:
            continue

        # 資源艦、他の艦隊に所属している、損傷を受けている、疲労がある、同じ艦を編成済みの場合は編成しない
        if (
            ship in resource_ships
            or ship.id in other_fleet_ship_ids
            or ship.damage > 0
            or ship.cond < 49
            or ship.ship_id in [s.ship_id for s in free_candidate + free_backup_escorts]
        ):
            continue

        # 工作艦は戦闘に向かないので編成しない
        if ship.stype == SType.RepairShip:
            continue

        # 海防艦は修理が早く終わるので最後に編成する
        if ship.stype == SType.Escort:
            free_backup_escorts.append(ship)
        else:
            free_candidate.append(ship)

        # 自由編成艦が2隻、バックアップ海防艦が2隻になったらループを抜ける
        if len(free_candidate) == 2 and len(free_backup_escorts) == 2:
            break

    if (
        len(free_candidate) + len(free_backup_destroyer) + len(free_backup_escorts)
    ) < 2:
        # 編成不可能なのでNoneを返す
        return None

    # 自由編成が2隻になっていない場合はバックアップ駆逐艦、バックアップ海防艦を追加する
    if len(free_candidate) < 2:
        free_candidate = (free_candidate + free_backup_destroyer + free_backup_escorts)[
            :2
        ]

    fleet = destroyer_candidate + free_candidate
    # 入渠コストの高い艦を旗艦にする
    high_cost_ship = sorted(
        fleet, key=lambda ship: (ndock_rate(ship), ship.lv), reverse=True
    )[0]
    fleet = [high_cost_ship] + [ship for ship in fleet if ship != high_cost_ship]
    print(f"編成します {[f.name for f in fleet]}")
    return [f.id for f in fleet]


async def handle_organize(fleet: list[int]):
    sorted_ship_list = sorted(
        ResponseMemory.port.ship_list, key=lambda ship: (-ship.lv, ship.sort_id)
    )
    max_page = math.ceil(len(sorted_ship_list) / 10)
    deck = ResponseMemory.port.deck_list[0]

    # 各艦のインデックスを取得
    index_list = [-1] * len(fleet)
    for i, id in enumerate(fleet):
        for j, ship in enumerate(sorted_ship_list):
            if ship.id == id:
                index_list[i] = j
                break

    await random_sleep()
    await click(ORGANIZATION)
    await wait_until_find(HOME_PORT_SCAN_TARGET)
    await random_sleep()
    await click(RELEASE_ESCORT)
    await random_sleep()

    current_page = 1
    for i, id in enumerate(fleet):
        # 旗艦が等しかった場合はスキップ
        if i == 0 and deck.ship_id_list[0] == id:
            continue

        await click(change_ship_button(i))
        await random_sleep()

        index = index_list[i]
        if index < (current_page - 1) * 10 or current_page * 10 <= index:
            new_page = math.floor(index / 10) + 1
            for from_the_left in calc_page_select_process(
                current_page=current_page,
                page_number=new_page,
                max_page=max_page,
            ):
                target = organization_page_from_the_left(from_the_left)
                await click(target)
                await random_sleep()
            current_page = new_page

        await click(organization_ship(index % 10))
        await random_sleep()
        await click(SHIP_CHANGE)
        await random_sleep()

    await click(HOME_PORT)
    while Context.page != Page.PORT:
        await asyncio.sleep(1)
    await wait_until_find(SETTING_SCAN_TARGET)
    if ResponseMemory.port.deck_list[0].ship_id_list != fleet:
        print("編成に失敗しました")
        exit()


async def handle_sortie(resource_ships: list[PortResponse.Ship]):
    if Context.skip_sortie:
        return False

    response = ResponseMemory.port
    fleet = calc_fleet(resource_ships)

    # 編成不可能な場合は離脱
    if fleet is None:
        return False

    # 編成を実施
    await handle_organize(fleet)

    # 遠征が帰ってきてる可能性があるので、チェック
    await handle_expedition_returned()

    # 補給が必要かどうか
    should_supply = any([response.get_ship(id).need_supply for id in fleet])

    async def _():
        if should_supply:
            await random_sleep()
            await supply()
        await sortie(fleet_size=len(fleet))

    Context.set_task(_)
    return True


async def handle_response(res: Response):
    if not res.url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return

    url = res.url

    if url.endswith("/api_port/port"):
        print("母港に到達しました")
        await Context.set_page_and_response(Page.PORT, res)

        resource_ships = calc_resource_ships()

        if await handle_sortie(resource_ships=resource_ships):
            return

        print("損傷感か疲労艦が含まれています。編成を行なってください。")
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


async def wait_command():
    while True:
        command = await asyncio.to_thread(input, "海域番号を受付中: ")
        command = command.split("-")
        try:
            maparea_id = int(command[0])
            mapinfo_no = int(command[1])
            SortieDestinationWrapper.maparea_id = maparea_id
            SortieDestinationWrapper.mapinfo_no = mapinfo_no
            break
        except:
            print("不正な入力です")


async def main():
    async with async_playwright() as p:
        await wait_command()

        await game_start(p, handle_response)

        input("Enterで出撃します🚨編成変更後に補給や疲労の確認を行いません")

        while True:
            await Context.do_task()
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())

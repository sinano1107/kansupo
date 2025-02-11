import asyncio
import math
from typing import Tuple
from playwright.async_api import async_playwright, Response

from scan.targets.targets import DEMOLITION_BUTTON_SCAN_TARGET, HOME_PORT_SCAN_TARGET
from ships.ship import Ship
from ships.ships import ships_map
from ships.needs_map import ship_needs_map
from targets.targets import (
    ARSENAL,
    DEMOLITION,
    DEMOLITION_BUTTON,
    HOME_PORT,
    demolition_page_from_the_left,
    demolition_ship,
)
from utils.calc_page_select_process import calc_page_select_process
from utils.click import click
from utils.context import Context, ResponseMemory, PortResponse
from utils.game_start import game_start
from utils.page import Page
from utils.random_sleep import random_sleep
from utils.wait_until_find import wait_until_find, wait_until_lost


def calc_resource_ships(ship_needs_map: dict[Ship, int] = ship_needs_map):
    """不要な艦(資源艦)を算出する"""
    # まずは保有艦を艦ごとに分類する
    shipid_ships_map: dict[int, list[PortResponse.Ship]] = {}
    for ship in ResponseMemory.port.ship_list:
        if ship.ship_id in shipid_ships_map:
            shipid_ships_map[ship.ship_id].append(ship)
        else:
            shipid_ships_map[ship.ship_id] = [ship]

    # 必要な艦のリストと照らし合わせて、不要な艦を算出する
    resource_ships: list[PortResponse.Ship] = []
    for ship_id, ships in shipid_ships_map.items():
        ship = ships_map[ship_id]
        if ship == None:
            raise ValueError("艦IDに対応する艦が存在しません")

        max_count = ship_needs_map.get(ship)
        if max_count == None:
            print(
                f"{ship.name}に対応する必要数が設定されていません。この艦は無限に保持します。"
            )
            max_count = math.inf

        if len(ships) > max_count:
            sorted_ships = sorted(ships, key=lambda ship: (-ship.lv, -ship.exp[0]))
            resource_ships.extend(sorted_ships[max_count:])

    for resource_ship in resource_ships[:]:  # resource_shipsのコピーを作成してループ
        if resource_ship.locked:
            print(
                f"{resource_ship.name}(lv={resource_ship.lv},id={resource_ship.id})はロックされています。そのため資源艦から外します"
            )
            resource_ships.remove(resource_ship)

    return resource_ships


def calc_demolition_process(
    resource_ships: list[PortResponse.Ship],
) -> Tuple[list[int], list[list[int]], list[int]]:
    """解体プロセスを算出する"""
    pages: list[int] = []
    indexes: list[list[int]] = []
    ship_counts: list[int] = []

    # shipsを並び替える
    sorted_ship_list = sorted(
        ResponseMemory.port.ship_list,
        key=lambda ship: (ship.lv, -ship.sort_id, ship.exp[0]),
    )

    max_page = math.ceil(len(sorted_ship_list) / 10)
    searching_page = 1
    while searching_page <= max_page:
        targets: list[int] = []
        for i, ship in enumerate(
            sorted_ship_list[(searching_page - 1) * 10 : searching_page * 10]
        ):
            if ship in resource_ships:
                targets.append(i)
        if len(targets) > 0:
            pages.append(searching_page)
            indexes.append(targets)
            for index in reversed(
                targets
            ):  # 前から削除するとずれてしまうので、後ろから削除する
                target = (searching_page - 1) * 10 + index
                sorted_ship_list.pop(target)
            ship_counts.append(len(sorted_ship_list))
        else:
            searching_page += 1

    return pages, indexes, ship_counts


async def handle_clean(resource_ships: list[PortResponse.Ship]):
    """最大艦船数に保持艦船数が近い場合、解体を行う"""

    response = ResponseMemory.port

    ships_count = len(response.ship_list)
    max_ships_count = response.basic.max_chara

    margin_count = 10
    if max_ships_count - margin_count <= ships_count:
        if len(resource_ships) < margin_count:
            raise ValueError("解体したとしても最大保有艦船数いっぱいに近いです")
        print("艦船数が最大艦船数に近いため解体を行います")

        async def _():
            pages, indexes, ship_counts = calc_demolition_process(
                resource_ships=resource_ships
            )

            await random_sleep()
            await click(ARSENAL)
            await wait_until_find(HOME_PORT_SCAN_TARGET)
            await random_sleep()
            await click(DEMOLITION)
            await random_sleep()

            current_page = 1
            current_ship_count = len(ResponseMemory.port.ship_list)
            for page, index, new_ship_count in zip(pages, indexes, ship_counts):
                max_page = math.ceil(current_ship_count / 10)

                # 現在のページと異なればページ選択を行う
                if current_page != page:
                    for from_the_left in calc_page_select_process(
                        current_page=current_page, page_number=page, max_page=max_page
                    ):
                        target = demolition_page_from_the_left(from_the_left)
                        await click(target)
                        await random_sleep()
                    current_page = page

                # 解体対象の艦をクリック
                for i in index:
                    await click(demolition_ship(i))
                    await random_sleep()

                # 解体ボタンをクリック
                await click(DEMOLITION_BUTTON)
                # 解体ボタンが消えるまで待つ
                await wait_until_lost(DEMOLITION_BUTTON_SCAN_TARGET)
                await random_sleep()

                current_ship_count = new_ship_count

            await click(HOME_PORT)

        Context.set_task(_)
        return True
    return False


async def handle_response(res: Response):
    if not res.url.startswith("http://w14h.kancolle-server.com/kcsapi/"):
        return

    url = res.url

    if url.endswith("/api_port/port"):
        print("母港に到達しました")
        await Context.set_page_and_response(Page.PORT, res)

        # 今後、バイト艦の選定などでresource_shipsは使用すると思うので、初めに算出しておく
        resource_ships = calc_resource_ships()

        if await handle_clean(resource_ships=resource_ships):
            return


async def main():
    async with async_playwright() as p:
        await game_start(p, handle_response=handle_response)

        while True:
            await Context.do_task()
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

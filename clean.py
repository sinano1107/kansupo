import math
from ships.ship import Ship
from ships.ships import ships_map
from ships.needs_map import ship_needs_map
from utils.context import ResponseMemory, PortResponse


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
            sorted_ships = sorted(ships, key=lambda ship: -ship.lv)
            resource_ships.extend(sorted_ships[max_count:])

    return resource_ships


async def handle_clean():
    """最大艦船数に保持艦船数が近い場合、解体を行う"""

    response = ResponseMemory.port

    ships_count = len(response.ship_list)
    max_ships_count = response.basic.max_chara

    if ships_count < max_ships_count - 5:
        print("艦船数が最大艦船数に近いため、解体を行います(未実装)")

    return False

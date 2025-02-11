import json

from ndock import calc_start_repair_data
from utils.context import PortResponse, ResponseMemory


def test_calc_start_repair_data():
    with open(
        "test_resources/ndock/2025-02-07 15:38:35.174047_api_port-port.json"
    ) as f:
        data = json.load(f).get("api_data")
        ResponseMemory.port = PortResponse.from_dict(data)

    response = ResponseMemory.port
    # 入渠中の艦のIDリストを取得
    repairing_ships_id_list = response.repairing_ships_id_list
    # 損傷艦のリストを作成
    damaged_ships = [ship for ship in response.ship_list if ship.damage > 0]
    # 入渠させるべき艦のリストを取得
    should_repair_ships = [
        ship for ship in damaged_ships if ship.id not in repairing_ships_id_list
    ]

    # 全True 入渠中なし
    should_use_dock_index_list, should_repair_ship_index_list = calc_start_repair_data(
        can_repair_count=10,
        is_ndock_empty_list=[True] * 10,
        damaged_ships=damaged_ships,
        should_repair_ships=should_repair_ships,
    )
    assert should_use_dock_index_list == [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
    ]
    assert should_repair_ship_index_list == [43, 35, 40, 0, 31, 30, 24, 28, 18, 22]

    # Trueまばら 入渠中なし
    random_ndock_empty_list = [
        True,
        False,
        False,
        True,
        True,
        False,
        True,
        True,
        True,
        True,
    ]
    should_use_dock_index_list, should_repair_ship_index_list = calc_start_repair_data(
        can_repair_count=5,
        is_ndock_empty_list=random_ndock_empty_list,
        damaged_ships=damaged_ships,
        should_repair_ships=should_repair_ships,
    )
    assert should_use_dock_index_list == [
        0,
        3,
        4,
        6,
        7,
    ]
    assert should_repair_ship_index_list == [43, 35, 40, 0, 31]

    # 全True 入渠中あり
    repairing_ships_id_list = [47, 177, 103, 106, 121]
    should_repair_ships = [
        ship for ship in damaged_ships if ship.id not in repairing_ships_id_list
    ]
    should_use_dock_index_list, should_repair_ship_index_list = calc_start_repair_data(
        can_repair_count=5,
        is_ndock_empty_list=[True] * 5,
        damaged_ships=damaged_ships,
        should_repair_ships=should_repair_ships,
    )
    assert should_use_dock_index_list == [0, 1, 2, 3, 4]
    assert should_repair_ship_index_list == [35, 31, 28, 18, 22]

    # Trueまばら 入渠中あり
    should_use_dock_index_list, should_repair_ship_index_list = calc_start_repair_data(
        can_repair_count=5,
        is_ndock_empty_list=random_ndock_empty_list,
        damaged_ships=damaged_ships,
        should_repair_ships=should_repair_ships,
    )
    assert should_use_dock_index_list == [0, 3, 4, 6, 7]
    assert should_repair_ship_index_list == [35, 31, 28, 18, 22]

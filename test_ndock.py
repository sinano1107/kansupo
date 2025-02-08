import json

from ndock import PageSelector, calc_start_repair_data
from utils.context import PortResponse, ResponseMemory


def test_PageSelector_calc_process():
    with open(
        "test_resources/ndock/2025-02-07 12:34:16.637291_api_port-port.json"
    ) as f:
        data = json.load(f).get("api_data")
        ResponseMemory.port = PortResponse.from_dict(data)
    assert PageSelector.calc_process(1, 1) == []
    assert PageSelector.calc_process(1, 2) == [2]
    assert PageSelector.calc_process(1, 3) == [3]
    assert PageSelector.calc_process(1, 4) == [4]
    assert PageSelector.calc_process(1, 5) == [5]
    assert PageSelector.calc_process(1, 6) == [5, 4]
    assert PageSelector.calc_process(1, 7) == [5, 5]
    assert PageSelector.calc_process(1, 8) == [5, 5, 4]
    assert PageSelector.calc_process(1, 9) == [5, 5, 5]
    assert PageSelector.calc_process(1, 10) == [5, 5, 5, 5]

    assert PageSelector.calc_process(10, 9) == [4]
    assert PageSelector.calc_process(10, 8) == [3]
    assert PageSelector.calc_process(10, 7) == [2]
    assert PageSelector.calc_process(10, 6) == [1]
    assert PageSelector.calc_process(10, 5) == [1, 2]
    assert PageSelector.calc_process(10, 4) == [1, 1]
    assert PageSelector.calc_process(10, 3) == [1, 1, 2]
    assert PageSelector.calc_process(10, 2) == [1, 1, 1]
    assert PageSelector.calc_process(10, 1) == [1, 1, 1, 1]

    assert PageSelector.calc_process(4, 5) == [4]


def test_calc_start_repair_data():
    with open(
        "test_resources/ndock/2025-02-07 15:38:35.174047_api_port-port.json"
    ) as f:
        data = json.load(f).get("api_data")
        ResponseMemory.port = PortResponse.from_dict(data)
    damaged_ships = [ship for ship in ResponseMemory.port.ship_list if ship.damage > 0]

    # 全True 入渠中なし
    should_use_dock_index_list, should_repair_ship_index_list = calc_start_repair_data(
        10, [True] * 10, damaged_ships, []
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
    should_use_dock_index_list, should_repair_ship_index_list = calc_start_repair_data(
        5,
        [True, False, False, True, True, False, True, True, True, True],
        damaged_ships,
        [],
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
    should_use_dock_index_list, should_repair_ship_index_list = calc_start_repair_data(
        5, [True] * 5, damaged_ships, [47, 177, 103, 106, 121]
    )
    assert should_use_dock_index_list == [0, 1, 2, 3, 4]
    assert should_repair_ship_index_list == [35, 31, 28, 18, 22]

    # Trueまばら 入渠中あり
    should_use_dock_index_list, should_repair_ship_index_list = calc_start_repair_data(
        5,
        [True, False, False, True, True, False, True, True, True, True],
        damaged_ships,
        [47, 177, 103, 106, 121],
    )
    assert should_use_dock_index_list == [0, 3, 4, 6, 7]
    assert should_repair_ship_index_list == [35, 31, 28, 18, 22]

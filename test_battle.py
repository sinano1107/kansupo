from copy import deepcopy
import json
from battle import calc_fleet, calc_remaining_hp
from utils.context import BattleResponse, PortResponse, ResponseMemory


def test_航空戦なし():
    with open(
        "test_resources/battle/2025-02-07 00:44:49.744704_api_req_sortie-battle.json"
    ) as f:
        data = json.load(f).get("api_data")
        ResponseMemory.battle = BattleResponse.from_dict(data)
    friend_remaining_hp_list, enemy_remaining_hp_list = calc_remaining_hp()
    assert friend_remaining_hp_list == [28, 16, 16, 14, 15]
    assert enemy_remaining_hp_list == [-28, -7, -48]


def test_航空戦あり():
    with open(
        "test_resources/battle/2025-02-07 00:45:56.617643_api_req_sortie-battle.json"
    ) as f:
        data = json.load(f).get("api_data")
        ResponseMemory.battle = BattleResponse.from_dict(data)
    friend_remaining_hp_list, enemy_remaining_hp_list = calc_remaining_hp()
    assert friend_remaining_hp_list == [28, 8, 16, 14, 15]
    assert enemy_remaining_hp_list == [36, -3, -54, -26, -56]


def test_calc_fleet():
    port = {
        "api_basic": {"api_max_chara": 100},
        "api_ship": [
            # 睦月
            {
                "api_id": 1,
                "api_ship_id": 1,
                "api_lv": 1,
                "api_nowhp": 28,
                "api_maxhp": 28,
                "api_fuel": 15,
                "api_bull": 15,
                "api_ndock_time": 0,
                "api_cond": 49,
                "api_locked": 1,
                "api_exp": [0, 100],
            },
            # 如月
            {
                "api_id": 2,
                "api_ship_id": 2,
                "api_lv": 1,
                "api_nowhp": 28,
                "api_maxhp": 28,
                "api_fuel": 15,
                "api_bull": 15,
                "api_ndock_time": 0,
                "api_cond": 49,
                "api_locked": 1,
                "api_exp": [0, 100],
            },
            # 長月
            {
                "api_id": 3,
                "api_ship_id": 6,
                "api_lv": 1,
                "api_nowhp": 28,
                "api_maxhp": 28,
                "api_fuel": 15,
                "api_bull": 15,
                "api_ndock_time": 0,
                "api_cond": 49,
                "api_locked": 1,
                "api_exp": [0, 100],
            },
            # 三日月
            {
                "api_id": 4,
                "api_ship_id": 7,
                "api_lv": 1,
                "api_nowhp": 28,
                "api_maxhp": 28,
                "api_fuel": 15,
                "api_bull": 15,
                "api_ndock_time": 0,
                "api_cond": 49,
                "api_locked": 1,
                "api_exp": [0, 100],
            },
            # 吹雪
            {
                "api_id": 5,
                "api_ship_id": 9,
                "api_lv": 1,
                "api_nowhp": 28,
                "api_maxhp": 28,
                "api_fuel": 15,
                "api_bull": 20,
                "api_ndock_time": 0,
                "api_cond": 49,
                "api_locked": 1,
                "api_exp": [0, 100],
            },
            # 白雪
            {
                "api_id": 6,
                "api_ship_id": 10,
                "api_lv": 1,
                "api_nowhp": 28,
                "api_maxhp": 28,
                "api_fuel": 15,
                "api_bull": 20,
                "api_ndock_time": 0,
                "api_cond": 49,
                "api_locked": 1,
                "api_exp": [0, 100],
            },
        ],
        "api_deck_port": [
            {
                "api_id": 1,
                "api_ship": [1, 2, 3, 4, 5, 6],
                "api_mission": [0, 0, 0, 0],
            }
        ],
        "api_ndock": [],
    }

    # 編成可能な駆逐艦6隻のみの場合
    ResponseMemory.port = PortResponse.from_dict(port)
    assert calc_fleet([]) == [1, 2, 3, 4, 5, 6]

    # lvが高い艦が混じった場合、そちらが旗艦に設定
    high_level_data = deepcopy(port)
    high_level_data.get("api_ship")[3]["api_lv"] = 2
    ResponseMemory.port = PortResponse.from_dict(high_level_data)
    assert calc_fleet([]) == [4, 1, 2, 3, 5, 6]

    # 低いcond値により、編成不可能な駆逐艦がいる場合
    low_cond_data = deepcopy(port)
    low_cond_data.get("api_ship")[0]["api_cond"] = 48
    ResponseMemory.port = PortResponse.from_dict(low_cond_data)
    assert calc_fleet([]) == None

    # 資源艦は弾かれることを確認
    assert calc_fleet([ResponseMemory.port.ship_list[0]]) == None

    # 低いcond値が含まれていても、他に候補が存在すればそちらが編成される
    low_cond_data.get("api_ship").append(
        {
            "api_id": 7,
            "api_ship_id": 11,  # 深雪
            "api_lv": 1,
            "api_nowhp": 28,
            "api_maxhp": 28,
            "api_fuel": 15,
            "api_bull": 20,
            "api_ndock_time": 0,
            "api_cond": 49,
            "api_locked": 1,
            "api_exp": [0, 100],
        }
    )
    ResponseMemory.port = PortResponse.from_dict(low_cond_data)
    assert calc_fleet([]) == [2, 3, 4, 5, 6, 7]

    # damageを受けていることによって、編成不可能な駆逐艦がいる場合
    low_hp_data = deepcopy(port)
    low_hp_data.get("api_ship")[0]["api_nowhp"] = (
        low_hp_data.get("api_ship")[0]["api_maxhp"] - 1
    )
    ResponseMemory.port = PortResponse.from_dict(low_hp_data)
    assert calc_fleet([]) == None

    # 他の艦隊に所属していて、編成不可能な駆逐艦がいる場合
    belong_to_another_fleet_data = deepcopy(port)
    # この操作はしなくてもテストは通るが、あり得ない状況なので追加
    belong_to_another_fleet_data.get("api_deck_port")[0].get("api_ship").remove(1)
    belong_to_another_fleet_data.get("api_deck_port").append(
        {
            "api_id": 2,
            "api_ship": [1],
            "api_mission": [0, 0, 0, 0],
        }
    )
    ResponseMemory.port = PortResponse.from_dict(belong_to_another_fleet_data)
    assert calc_fleet([]) == None

    # 駆逐艦5隻と工作艦しかいない場合
    repair_ship_data = deepcopy(port)
    repair_ship_data["api_ship"].pop()
    repair_ship_data["api_ship"].append(
        {
            "api_id": 7,
            "api_ship_id": 182,  # 明石
            "api_lv": 1,
            "api_nowhp": 28,
            "api_maxhp": 28,
            "api_fuel": 50,
            "api_bull": 10,
            "api_ndock_time": 0,
            "api_cond": 49,
            "api_locked": 1,
            "api_exp": [0, 100],
        }
    )
    ResponseMemory.port = PortResponse.from_dict(repair_ship_data)
    assert calc_fleet([]) == None

    # 駆逐艦4隻と軽巡2隻しかいない場合
    light_cruiser_data = deepcopy(port)
    light_cruiser_data.get("api_ship").pop()
    light_cruiser_data.get("api_ship").pop()
    light_cruiser_data.get("api_ship").extend(
        [
            {
                "api_id": 7,
                "api_ship_id": 22,  # 五十鈴
                "api_lv": 1,
                "api_nowhp": 28,
                "api_maxhp": 28,
                "api_fuel": 50,
                "api_bull": 10,
                "api_ndock_time": 0,
                "api_cond": 49,
                "api_locked": 1,
                "api_exp": [0, 100],
            },
            {
                "api_id": 8,
                "api_ship_id": 23,  # 由良
                "api_lv": 1,
                "api_nowhp": 28,
                "api_maxhp": 28,
                "api_fuel": 50,
                "api_bull": 10,
                "api_ndock_time": 0,
                "api_cond": 49,
                "api_locked": 1,
                "api_exp": [0, 100],
            },
        ]
    )
    ResponseMemory.port = PortResponse.from_dict(light_cruiser_data)
    assert calc_fleet([]) == [1, 2, 3, 4, 7, 8]

    # 駆逐艦が足りない場合駆逐艦3隻と軽巡2隻しかいない場合
    light_cruiser_data.get("api_ship").pop(0)
    ResponseMemory.port = PortResponse.from_dict(light_cruiser_data)
    assert calc_fleet([]) == None

    # 駆逐艦3隻と軽巡3隻の場合
    light_cruiser_data.get("api_ship").append(
        {
            "api_id": 9,
            "api_ship_id": 24,  # 大井
            "api_lv": 1,
            "api_nowhp": 28,
            "api_maxhp": 28,
            "api_fuel": 50,
            "api_bull": 10,
            "api_ndock_time": 0,
            "api_cond": 49,
            "api_locked": 1,
            "api_exp": [0, 100],
        }
    )
    assert calc_fleet([]) == None

    # 重巡洋艦が混じった場合、重巡洋艦が旗艦に設定
    heavy_cruiser_data = deepcopy(port)
    heavy_cruiser_data.get("api_ship").pop()
    heavy_cruiser_data.get("api_ship").append(
        {
            "api_id": 7,
            "api_ship_id": 66,  # 高尾
            "api_lv": 1,
            "api_nowhp": 28,
            "api_maxhp": 28,
            "api_fuel": 50,
            "api_bull": 10,
            "api_ndock_time": 0,
            "api_cond": 49,
            "api_locked": 1,
            "api_exp": [0, 100],
        }
    )
    ResponseMemory.port = PortResponse.from_dict(heavy_cruiser_data)
    assert calc_fleet([]) == [7, 1, 2, 3, 4, 5]

    # 自由艦に分類される艦を資源艦に指定した場合も編成不可能
    assert calc_fleet([ResponseMemory.port.ship_list[5]]) == None

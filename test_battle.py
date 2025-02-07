import json
from battle import calc_remaining_hp
from utils.context import BattleResponse, ResponseMemory


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

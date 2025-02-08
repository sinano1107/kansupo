import json
import math

from clean import calc_resource_ships
from utils.context import PortResponse, ResponseMemory
from ships.ships import 龍田, 川内, 川内改


def test_calc_resource_ships():
    with open("test_resources/clean/port_1.txt") as f:
        data = json.loads(f.read()).get("api_data")
        ResponseMemory.port = PortResponse.from_dict(data)

    # 必要数の指定なし
    ship_needs_map = {}
    resource_ships = calc_resource_ships(ship_needs_map=ship_needs_map)
    assert resource_ships == []

    # 必要数の指定あり
    ship_needs_map = {龍田: 1}
    resource_ships = calc_resource_ships(ship_needs_map=ship_needs_map)
    assert len(resource_ships) == 1
    assert resource_ships[0].ship_id == 龍田.id
    # lvが低い方が資源艦として優先されることを確認
    assert resource_ships[0].lv == 1

    # 改造艦の判定が分かれていることを確認
    ship_needs_map = {川内改: 1, 川内: 0}
    resource_ships = calc_resource_ships(ship_needs_map=ship_needs_map)
    assert len(resource_ships) == 1
    assert resource_ships[0].ship_id == 川内.id
    assert resource_ships[0].ship_id != 川内改.id

    # math.infを指定する場合
    ship_needs_map = {龍田: math.inf}
    resource_ships = calc_resource_ships(ship_needs_map=ship_needs_map)
    assert resource_ships == []

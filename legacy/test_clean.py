import json
import math

from clean import calc_demolition_process, calc_resource_ships
from utils.context import PortResponse, ResponseMemory
from ships.ships import (
    龍田,
    川内,
    川内改,
    吹雪改,
    松輪,
    択捉,
    不知火,
    満潮,
    朝潮,
    山風,
    村雨,
    白露,
    那珂,
    由良,
    球磨,
    加古,
    長鯨,
    清霜,
    早霜,
    秋雲,
    黒潮,
    霰,
    荒潮,
    子日,
    初春,
    漣,
    朧,
    望月,
    長月,
    長良,
    瑞穂,
    大潮,
    涼風,
    五月雨,
    潮,
    若葉,
    敷波,
    名取,
    菊月,
    鳳翔,
    初霜,
    曙,
    磯波,
    叢雲,
    深雪,
    雷,
    初雪,
    三日月,
    文月,
    皐月,
    如月,
    睦月,
    木曾,
    天龍,
    電,
    古鷹,
    暁,
    神通,
    北上改,
    多摩,
    霞,
    時雨改,
    響改,
    綾波改,
    白雪改,
    夕立改,
    祥鳳改,
)


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

    # ロック艦は資源艦から外されることを確認
    ship_needs_map = {吹雪改: 0}
    resource_ships = calc_resource_ships(ship_needs_map=ship_needs_map)
    assert resource_ships == []


def test_calc_demolition_process():
    with open("test_resources/clean/port_2.json") as f:
        data = json.loads(f.read()).get("api_data")
        ResponseMemory.port = PortResponse.from_dict(data)

    # 資源艦なしの場合
    resource_ships = calc_resource_ships(ship_needs_map={})
    pages, indexes, ship_counts = calc_demolition_process(resource_ships=resource_ships)
    assert pages == []
    assert indexes == []

    # 全て資源艦の場合
    ship_needs_map = {
        松輪: 0,
        択捉: 0,
        不知火: 0,
        満潮: 0,
        朝潮: 0,
        山風: 0,
        村雨: 0,
        白露: 0,
        那珂: 0,
        由良: 0,
        球磨: 0,
        加古: 0,
        長鯨: 0,
        清霜: 0,
        早霜: 0,
        秋雲: 0,
        黒潮: 0,
        霰: 0,
        荒潮: 0,
        子日: 0,
        初春: 0,
        漣: 0,
        朧: 0,
        望月: 0,
        長月: 0,
        長良: 0,
        瑞穂: 0,
        大潮: 0,
        涼風: 0,
        五月雨: 0,
        潮: 0,
        若葉: 0,
        敷波: 0,
        名取: 0,
        菊月: 0,
        鳳翔: 0,
        初霜: 0,
        曙: 0,
        磯波: 0,
        叢雲: 0,
        深雪: 0,
        雷: 0,
        龍田: 0,
        初雪: 0,
        三日月: 0,
        文月: 0,
        皐月: 0,
        如月: 0,
        睦月: 0,
        木曾: 0,
        天龍: 0,
        電: 0,
        古鷹: 0,
        暁: 0,
        神通: 0,
        北上改: 0,
        多摩: 0,
        霞: 0,
        時雨改: 0,
        響改: 0,
        綾波改: 0,
        白雪改: 0,
        夕立改: 0,
        川内改: 0,
        吹雪改: 0,
        祥鳳改: 0,
    }
    resource_ships = calc_resource_ships(ship_needs_map=ship_needs_map)
    pages, indexes, ship_counts = calc_demolition_process(resource_ships=resource_ships)
    assert pages == [1, 1, 1, 1, 1, 1, 1]
    assert indexes == [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    ]
    assert ship_counts == [60, 50, 40, 30, 20, 10, 0]

    # 適当に資源艦を指定
    ship_needs_map = {
        松輪: math.inf,
        択捉: math.inf,
        不知火: math.inf,
        満潮: math.inf,
        朝潮: math.inf,
        山風: math.inf,
        村雨: math.inf,
        白露: math.inf,
        那珂: 0,
        由良: math.inf,
        球磨: math.inf,
        加古: math.inf,
        長鯨: math.inf,
        清霜: math.inf,
        早霜: 1,
        秋雲: 1,
        黒潮: 1,
        霰: 0,
        荒潮: 0,
        子日: 0,
        初春: 1,
        漣: 1,
        朧: 1,
        望月: 1,
        長月: 1,
        長良: 1,
        瑞穂: 1,
        大潮: 1,
        涼風: 1,
        五月雨: 1,
        潮: 1,
        若葉: 1,
        敷波: 1,
        名取: 1,
        菊月: 1,
        鳳翔: 1,
        初霜: 1,
        曙: 0,
        磯波: 0,
        叢雲: 0,
        深雪: 1,
        雷: 1,
        龍田: 1,
        初雪: 1,
        三日月: 1,
        文月: 0,
        皐月: 0,
        如月: 0,
        睦月: 0,
        木曾: 0,
        天龍: 1,
        電: 1,
        古鷹: 1,
        暁: 1,
        神通: 1,
        北上改: 0,
        多摩: 0,
        霞: 0,
        時雨改: 0,
        響改: 0,
        綾波改: 1,
        白雪改: 1,
        夕立改: 1,
        川内改: 1,
        吹雪改: 1,
        祥鳳改: 0,
    }
    resource_ships = calc_resource_ships(ship_needs_map=ship_needs_map)
    print([ship.name for ship in resource_ships])
    pages, indexes, ship_counts = calc_demolition_process(resource_ships=resource_ships)
    assert pages == [1, 2, 2, 4, 5, 5, 5, 6]
    assert indexes == [
        [9],
        [7, 8],
        [8],
        [7, 8, 9],
        [2, 3, 4, 5, 6],
        [7, 8, 9],
        [7, 8],
        [2],
    ]
    assert ship_counts == [69, 67, 66, 63, 58, 55, 53, 52]

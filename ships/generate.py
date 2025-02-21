import json
from playwright.async_api import Response


async def generate_ships(response: Response):
    """艦のマスターデータをPythonコードとして生成する"""
    data = json.loads((await response.body())[7:]).get("api_data")

    ship_list = data.get("api_mst_ship")

    # 駆逐艦イ級以前に味方艦の情報が格納されているので、それのインデックスを取得する
    end_index = None
    # 開発時点でのイ級のインデックス以降を探索する
    for i in range(792, len(ship_list)):
        if ship_list[i].get("api_id") == 1501:
            end_index = i
            break
    ship_list = ship_list[:end_index]

    ships_str = ""
    dict_str = ""

    for ship in ship_list:
        id = ship.get("api_id")
        name = ship.get("api_name")
        replaced_name = name.replace(" ", "_").replace("-", "_").replace(".", "_")
        fuel_max = ship.get("api_fuel_max")
        bull_max = ship.get("api_bull_max")
        sort_id = ship.get("api_sort_id")
        stype = ship.get("api_stype")
        ships_str += f"{replaced_name} = Ship({id=}, {name=}, {fuel_max=}, {bull_max=}, {sort_id=}, {stype=})\n"
        dict_str += f"\t{id}: {replaced_name},\n"

    with open("ships/ships.py", "w") as f:
        f.write(
            f"from .ship import Ship\n\n\n{ships_str}\n\nships_map = {{\n{dict_str}}}"
        )

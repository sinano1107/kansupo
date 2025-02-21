from time import time
from dataclasses import dataclass, field
from enum import IntEnum
from dataclasses_json import config, dataclass_json


class MissionState(IntEnum):
    """任務の状態を表す列挙型"""

    # 未出撃
    NOT_STARTED = 0
    # 遠征中
    IN_PROGRESS = 1
    # 遠征帰投
    COMPLETED = 2
    # 強制帰投中
    FORCED_RETURN = 3


@dataclass_json
@dataclass(frozen=True)
class Deck:
    id: int = field(metadata=config(field_name="api_id"))
    ship_id_list: list[int] = field(metadata=config(field_name="api_ship"))
    mission: list[int] = field(metadata=config(field_name="api_mission"))

    @property
    def mission_state(self) -> MissionState:
        return self.mission[0]

    @property
    def seconds_until_mission_end(self) -> int:
        """遠征終了までの秒数"""
        if (
            self.mission_state != MissionState.IN_PROGRESS
            and self.mission_state != MissionState.FORCED_RETURN
        ):
            return None
        return self.mission[2] / 1000 - time() - 60


@dataclass(frozen=True)
class Ship:
    id: int = field(metadata=config(field_name="api_id"))
    ship_id: int = field(metadata=config(field_name="api_ship_id"))
    fuel: int = field(metadata=config(field_name="api_fuel"))
    bull: int = field(metadata=config(field_name="api_bull"))
    maxhp: int = field(metadata=config(field_name="api_maxhp"))
    nowhp: int = field(metadata=config(field_name="api_nowhp"))
    ndock_time: int = field(metadata=config(field_name="api_ndock_time"))
    cond: int = field(metadata=config(field_name="api_cond"))
    lv: int = field(metadata=config(field_name="api_lv"))
    exp: list[int] = field(metadata=config(field_name="api_exp"))
    locked: bool = field(metadata=config(field_name="api_locked"))

    @property
    def mst(self):
        from ships.ships import ships_map

        res = ships_map.get(self.ship_id)
        if res is None:
            raise ValueError(f"艦ID{self.ship_id}に対応する艦が存在しません")
        return res

    @property
    def damage(self):
        """ダメージ"""
        return self.maxhp - self.nowhp

    @property
    def name(self):
        """艦名"""
        return self.mst.name

    @property
    def sort_id(self):
        """sort_id"""
        return self.mst.sort_id

    @property
    def need_supply(self):
        """補給を必要としているか"""
        return self.fuel < self.mst.fuel_max or self.bull < self.mst.bull_max

    @property
    def stype(self):
        """艦種"""
        return self.mst.stype


@dataclass_json
@dataclass(frozen=True)
class PortResponse:
    deck_list: list[Deck] = field(metadata=config(field_name="api_deck_port"))
    ship_list: list[Ship] = field(metadata=config(field_name="api_ship"))

    @property
    def waiting_mission_deck(self) -> Deck:
        """遠征待機中の艦隊"""
        for deck in self.deck_list[1:]:
            if deck.mission_state == MissionState.NOT_STARTED:
                return deck

    def get_ship(self, id: int):
        """idから艦を取得する"""
        for ship in self.ship_list:
            if ship.id == id:
                return ship
        raise ValueError(f"{id=} に対応する艦船が存在しません")

    def is_supply_needed(self, fleet_number: int) -> bool:
        """補給が必要かどうか"""
        if fleet_number < 0 or fleet_number > len(self.deck_list):
            raise ValueError(f"{fleet_number=} に対応する艦隊が存在しません")

        for ship_id in self.deck_list[fleet_number - 1].ship_id_list:
            if ship_id == -1:
                # スロットを開けて艦を編成することはできないので、-1の場合はブレイクする
                break
            ship = self.get_ship(ship_id)
            if ship.need_supply:
                return True
        return False

    @property
    def seconds_until_mission_end(self):
        """全ての遠征艦隊の中で最も早く帰投する艦隊の帰投までの秒数"""
        array = [deck.seconds_until_mission_end for deck in self.deck_list[1:]]
        array = [a for a in array if a is not None]
        return min(array) if array else None

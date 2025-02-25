from logging import getLogger, Logger
from time import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import ClassVar
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
    def hp_ratio(self):
        """HPの割合"""
        return self.nowhp / self.maxhp

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

    def __str__(self):
        return f"{self.name}(lv={self.lv},id={self.id})"


class NDockState(IntEnum):
    """入渠の状態を表す列挙型"""

    # ロック(?)
    LOCKED = -1
    # 空き
    EMPTY = 0
    # 入渠中
    IN_PROGRESS = 1


@dataclass(frozen=True)
class NDock:
    id: int = field(metadata=config(field_name="api_id"))
    state: NDockState = field(metadata=config(field_name="api_state"))
    ship_id: int = field(metadata=config(field_name="api_ship_id"))
    complete_time: int = field(metadata=config(field_name="api_complete_time"))


@dataclass_json
@dataclass
class PortResponse:
    logger: ClassVar[Logger] = getLogger("uvicorn.page_controllers.port.response")
    _resource_ships: ClassVar[list[Ship]] = None
    _ships_needing_repair: ClassVar[list[Ship]] = None
    _ships_sorted_by_damage_ratio: ClassVar[list[Ship]] = None

    deck_list: list[Deck] = field(metadata=config(field_name="api_deck_port"))
    ship_list: list[Ship] = field(metadata=config(field_name="api_ship"))
    ndock_list: list[NDock] = field(metadata=config(field_name="api_ndock"))

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

    @property
    def seconds_until_repair_end(self):
        """全ての入渠中の艦の中で最も早く入渠が終了する艦の入渠終了までの秒数"""
        array = [
            ndock.complete_time
            for ndock in self.ndock_list
            if ndock.state == NDockState.IN_PROGRESS
        ]
        return min(array) / 1000 - time() - 60 if array else None

    @property
    def ships_sorted_by_damage_ratio(self) -> list[Ship]:
        """hp割合によりソートした艦のリスト"""
        if self._ships_sorted_by_damage_ratio is None:
            self._ships_sorted_by_damage_ratio = sorted(
                self.ship_list, key=lambda ship: (ship.hp_ratio, ship.sort_id)
            )
        return self._ships_sorted_by_damage_ratio

    @property
    def repairing_ship_id_list(self):
        """入渠中の艦のIDリスト"""
        return [ndock.ship_id for ndock in self.ndock_list if ndock.state == 2]

    @property
    def ships_needing_repair(self) -> list[Ship]:
        """入渠が必要な艦のリスト"""
        if self._ships_needing_repair is None:
            self._ships_needing_repair = [
                ship
                for ship in self.ship_list
                if ship.damage > 0  # ダメージがある
                and ship not in self.resource_ships  # 資源艦でない
                and ship.id not in self.repairing_ship_id_list  # 入渠中でない
            ]
            self._ships_needing_repair = list(
                sorted(self._ships_needing_repair, key=lambda ship: ship.ndock_time)
            )
        return self._ships_needing_repair

    @property
    def is_repair_needed(self):
        """入渠が必要かどうか"""
        return bool(self.ships_needing_repair)

    @property
    def can_repair(self):
        """入渠可能かどうか"""
        for ndock in self.ndock_list:
            if ndock.state == NDockState.EMPTY:
                return True
        return False

    @property
    def resource_ships(self):
        """不要な艦(資源艦)を算出する"""
        if self._resource_ships is None:
            from ships.needs_map import ship_needs_map

            # 保有艦をidごとに分類する
            shipid_to_ships_map: dict[int, list[Ship]] = {}
            for ship in self.ship_list:
                if ship.ship_id in shipid_to_ships_map:
                    shipid_to_ships_map[ship.ship_id].append(ship)
                else:
                    shipid_to_ships_map[ship.ship_id] = [ship]

            # 必要な艦のリストと照らし合わせて、不要な艦を算出する
            resource_ships: list[Ship] = []
            for ship_id, ships in shipid_to_ships_map.items():
                ship = ships[0].mst
                max_count = ship_needs_map.get(ship)
                if max_count is None:
                    self.logger.info(
                        f"{ship.name}に対応する必要数が設定されていません。この艦は無限に保持します"
                    )
                    max_count = float("inf")

                if len(ships) > max_count:
                    sorted_ships = sorted(
                        ships, key=lambda ship: (-ship.lv, -ship.exp[0])
                    )
                    resource_ships.extend(sorted_ships[max_count:])

            # ロックされている艦を除外する
            for resource_ship in resource_ships[:]:
                if resource_ship.locked:
                    self.logger.info(
                        f"{resource_ship.name}(lv={resource_ship.lv},id={resource_ship.id})はロックされているため資源艦から外します"
                    )
                    resource_ships.remove(resource_ship)

            self._resource_ships = resource_ships
        return self._resource_ships

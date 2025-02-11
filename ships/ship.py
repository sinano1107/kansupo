from dataclasses import dataclass
from enum import IntEnum


class SType(IntEnum):
    # 海防艦
    Escort = 1
    # 駆逐艦
    Destroyer = 2
    # 軽巡洋艦
    LightCruiser = 3
    # 重雷装艦(重雷装巡洋艦)
    TorpedoCruiser = 4
    # 重巡洋艦
    HeavyCruiser = 5
    # 航空巡洋艦
    AircraftCruiser = 6
    # 軽空母
    LightAircraftCarrier = 7
    # 巡洋戦艦
    BattleCruiser = 8
    # 戦艦
    Battleship = 9
    # 航空戦艦
    AircraftBattleship = 10
    # 空母
    AircraftCarrier = 11
    # 潜水艦
    Submarine = 13
    # 潜水空母
    SubmarineAircraftCarrier = 14
    # 水上機母艦
    SeaplaneCarrier = 16
    # 強襲揚陸艦
    AmphibiousAssaultShip = 17
    # 装甲空母
    ArmoredAircraftCarrier = 18
    # 工作艦
    RepairShip = 19
    # 潜水母艦
    SubmarineTender = 20
    # 練習巡洋艦
    TrainingCruiser = 21
    # 補給艦
    SupplyShip = 22


@dataclass(frozen=True)
class Ship:
    """
    艦の情報を表現するクラス
    
    fuel_max: 燃料の最大値
    bull_max: 弾薬の最大値
    """
    id: int
    name: str
    fuel_max: int
    bull_max: int
    sort_id: int
    stype: SType

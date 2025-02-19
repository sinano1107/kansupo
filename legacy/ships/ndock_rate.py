from ships.ship import SType, Ship
from ships.ships import Гангут


def ndock_rate(ship: Ship) -> float:
    """入渠にかかる時間の計算に用いる「倍率」を返す
    参考:https://wikiwiki.jp/kancolle/%E5%85%A5%E6%B8%A0
    """
    stype = ship.stype
    if (
        # 潜水艦
        stype == SType.Submarine
        # 海防艦
        or stype == SType.Escort
    ):
        return 0.5
    if (
        # 駆逐艦
        stype == SType.Destroyer
        # 軽巡洋艦
        or stype == SType.LightCruiser
        # 重雷装艦(重雷装巡洋艦)
        or stype == SType.TorpedoCruiser
        # 練習巡洋艦
        or stype == SType.TrainingCruiser
        # 水上機母艦
        or stype == SType.SeaplaneCarrier
        # 潜水空母
        or stype == SType.SubmarineAircraftCarrier
        # 揚陸艦
        or stype == SType.AmphibiousAssaultShip
        # 補給艦
        or stype == SType.SupplyShip
    ):
        return 1
    if (
        # 重巡洋艦
        stype == SType.HeavyCruiser
        # 航空巡洋艦
        or stype == SType.AircraftCruiser
        # 高速戦艦
        or stype == SType.Battleship
        # 軽空母
        or stype == SType.LightAircraftCarrier
        # 潜水母艦
        or stype == SType.SubmarineTender
        # Гангут
        or ship.id == Гангут.id
    ):
        return 1.5
    if (
        # Гангут以外の戦艦
        stype == SType.Battleship
        # 航空戦艦
        or stype == SType.AircraftBattleship
        # 正規空母
        or stype == SType.AircraftCarrier
        # 装甲空母
        or stype == SType.ArmoredAircraftCarrier
        # 工作艦
        or stype == SType.RepairShip
    ):
        return 2

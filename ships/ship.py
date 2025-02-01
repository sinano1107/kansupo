from dataclasses import dataclass


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
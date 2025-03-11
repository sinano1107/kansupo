from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import config, dataclass_json


@dataclass_json
@dataclass(frozen=True)
class MapNextResponse:
    # 次のセルから派生しているセルの個数
    next: int = field(metadata=config(field_name="api_next"))
    event_id: int = field(metadata=config(field_name="api_event_id"))
    rashin_flag: bool = field(metadata=config(field_name="api_rashin_flg"))
    event_id: int = field(metadata=config(field_name="api_event_id"))


@dataclass_json
@dataclass(frozen=True)
class BattleResponse:

    @dataclass(frozen=True)
    class Kouku:
        @dataclass(frozen=True)
        class Stage3:
            fdam: list[float] = field(metadata=config(field_name="api_fdam"))
            edam: list[float] = field(metadata=config(field_name="api_edam"))

        stage3: Optional[Stage3] = field(metadata=config(field_name="api_stage3"))

    @dataclass(frozen=True)
    class Hougeki:
        # Trueだったら敵からの攻撃
        at_eflag_list: list[bool] = field(metadata=config(field_name="api_at_eflag"))
        df_list: list[list[int]] = field(metadata=config(field_name="api_df_list"))
        damage_list: list[list[float]] = field(metadata=config(field_name="api_damage"))

    @dataclass(frozen=True)
    class Raigeki:
        fdam: list[float] = field(metadata=config(field_name="api_fdam"))
        edam: list[float] = field(metadata=config(field_name="api_edam"))

    hourai_flag: list[bool] = field(metadata=config(field_name="api_hourai_flag"))
    friend_now_hp_list: list[int] = field(metadata=config(field_name="api_f_nowhps"))
    enemy_now_hp_list: list[int] = field(metadata=config(field_name="api_e_nowhps"))
    friend_max_hp_list: list[int] = field(metadata=config(field_name="api_f_maxhps"))
    # 航空戦フラグ [n]=0 のとき api_stage<n+1>=null になる(航空戦力なし, 艦戦のみなど)
    stage_flag: list[bool] = field(metadata=config(field_name="api_stage_flag"))
    kouku: Kouku = field(metadata=config(field_name="api_kouku"))
    opening_taisen_flag: bool = field(
        metadata=config(field_name="api_opening_taisen_flag")
    )
    opening_flag: bool = field(metadata=config(field_name="api_opening_flag"))
    hougeki1: Hougeki = field(metadata=config(field_name="api_hougeki1"))
    hougeki2: Optional[Hougeki] = field(metadata=config(field_name="api_hougeki2"))
    hougeki3: Optional[Hougeki] = field(metadata=config(field_name="api_hougeki3"))
    raigeki: Optional[Raigeki] = field(metadata=config(field_name="api_raigeki"))


@dataclass_json
@dataclass(frozen=True)
class MidnightBattleResponse:
    friend_now_hp_list: list[int] = field(metadata=config(field_name="api_f_nowhps"))
    friend_max_hp_list: list[int] = field(metadata=config(field_name="api_f_maxhps"))
    hougeki: BattleResponse.Hougeki = field(metadata=config(field_name="api_hougeki"))


@dataclass_json
@dataclass(frozen=True)
class BattleResultResponse:
    @dataclass(frozen=True)
    class GetShip:
        name: str = field(metadata=config(field_name="api_ship_name"))

    get_flag: list[bool, bool] = field(metadata=config(field_name="api_get_flag"))
    get_ship: Optional[GetShip] = field(
        default=None, metadata=config(field_name="api_get_ship")
    )

import asyncio
from dataclasses import dataclass, field
import json
from typing import Coroutine, Optional

from dataclasses_json import config, dataclass_json
from utils.page import Page
from playwright.async_api import Locator, Response


@dataclass_json
@dataclass(frozen=True)
class PortResponse:
    @dataclass(frozen=True)
    class Ship:
        id: int = field(metadata=config(field_name="api_id"))
        ship_id: int = field(metadata=config(field_name="api_ship_id"))
        fuel: int = field(metadata=config(field_name="api_fuel"))
        bull: int = field(metadata=config(field_name="api_bull"))
        maxhp: int = field(metadata=config(field_name="api_maxhp"))
        nowhp: int = field(metadata=config(field_name="api_nowhp"))
        
        @property
        def damage(self):
            return self.maxhp - self.nowhp
    
    @dataclass(frozen=True)
    class Deck:
        ship_id_list: list[int] = field(metadata=config(field_name="api_ship"))
    
    # 所持艦船リスト
    ship_list: list[Ship] = field(metadata=config(field_name="api_ship"))
    deck_port: list[Deck] = field(metadata=config(field_name="api_deck_port"))


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
    opening_taisen_flag: bool = field(metadata=config(field_name="api_opening_taisen_flag"))
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
    get_ship: Optional[GetShip] = field(default=None, metadata=config(field_name="api_get_ship"))


class ResponseMemory:
    port: PortResponse = None
    map_next: MapNextResponse = None
    battle: BattleResponse = None
    midnight_battle: MidnightBattleResponse = None
    battle_result: BattleResultResponse = None
    
    @staticmethod
    def extraction_data(response: bytes):
        json_data = json.loads(response[7:])
        if json_data.get("api_result") != 1:
            raise ValueError("APIが失敗したようです")
        return json_data.get("api_data")
    
    @classmethod
    async def set_response(cls, page: Page, response: Response):
        data = cls.extraction_data(await response.body())
        if page == Page.PORT:
            cls.port = PortResponse.from_dict(data)
        elif page == Page.SORTIE_START or page == Page.GOING_TO_NEXT_CELL:
            cls.map_next = MapNextResponse.from_dict(data)
        elif page == Page.BATTLE:
            cls.battle = BattleResponse.from_dict(data)
        elif page == Page.MIDNIGHT_BATTLE:
            cls.midnight_battle = MidnightBattleResponse.from_dict(data)
        elif page == Page.BATTLE_RESULT:
            cls.battle_result = BattleResultResponse.from_dict(data)
        else:
            raise ValueError(f"レスポンスの解析が設定されていないページです {page=}")


class Context:
    canvas: Locator = None
    page: Page = Page.START
    wait_task: asyncio.Task = None
    task: Coroutine = None
    
    @classmethod
    async def do_task(cls):
        if cls.task is None:
            print("タスクが設定されていません")
        else:
            await cls.task()
            cls.task = None
    
    @classmethod
    def set_page(cls, page: Page):
        cls.page = page
    
    @classmethod
    async def set_page_and_response(cls, page: Page, response: Response):
        await ResponseMemory.set_response(page, response)
        cls.set_page(page)
    
    @classmethod
    def set_task(cls, task: Coroutine):
        if cls.task is not None:
            print("タスクが存在するため設定しません")
            return
        cls.task = task
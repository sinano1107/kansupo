import asyncio
from dataclasses import dataclass, field
from enum import IntEnum
import json
from typing import Coroutine, Optional
from dataclasses_json import config, dataclass_json

from utils.page import Page
from playwright.async_api import Locator, Response


@dataclass_json
@dataclass(frozen=True)
class PortResponse:

    @dataclass(frozen=True)
    class Basic:
        max_chara: int = field(metadata=config(field_name="api_max_chara"))

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
                raise ValueError(f"艦ID{self.ship_id}に対忋する艦が存在しません")
            return res

        @property
        def damage(self):
            return self.maxhp - self.nowhp

        @property
        def name(self):
            return self.mst.name

        @property
        def sort_id(self):
            return self.mst.sort_id

        @property
        def need_supply(self):
            return self.fuel < self.mst.fuel_max or self.bull < self.mst.bull_max

        @property
        def stype(self):
            return self.mst.stype

    @dataclass(frozen=True)
    class Deck:
        id: int = field(metadata=config(field_name="api_id"))
        ship_id_list: list[int] = field(metadata=config(field_name="api_ship"))
        mission: list[int] = field(metadata=config(field_name="api_mission"))

        class MissionState(IntEnum):
            # 未出撃
            NotDispatched = 0
            # 遠征中
            OnAnExpedition = 1
            # 遠征帰投
            ExpeditionReturned = 2
            # 強制帰投中
            ForcedReturn = 3

        @property
        def mission_state(self) -> MissionState:
            return self.mission[0]

    @dataclass(frozen=True)
    class NDock:
        id: int = field(metadata=config(field_name="api_id"))
        state: int = field(metadata=config(field_name="api_state"))
        ship_id: int = field(metadata=config(field_name="api_ship_id"))
        complete_time: int = field(metadata=config(field_name="api_complete_time"))

    basic: Basic = field(metadata=config(field_name="api_basic"))
    # 所持艦船リスト
    ship_list: list[Ship] = field(metadata=config(field_name="api_ship"))
    deck_list: list[Deck] = field(metadata=config(field_name="api_deck_port"))
    ndock_list: list[NDock] = field(metadata=config(field_name="api_ndock"))

    @property
    def ndock_empty_flag_list(self):
        """空いているドックのインデックスのみTrueのリスト"""
        return [ndock.state == 0 for ndock in self.ndock_list]

    @property
    def repairing_ships_id_list(self):
        """入渠中の艦のIDリスト"""
        return list(
            map(
                lambda ndock: ndock.ship_id,
                filter(lambda ndock: ndock.state == 1, self.ndock_list),
            )
        )

    @property
    def has_repair_ship(self):
        """修理すべき艦を持っているか(修理中の艦は除く)"""
        repairing_ship_id_list = self.repairing_ships_id_list
        for ship in self.ship_list:
            if ship.ndock_time != 0 and ship.id not in repairing_ship_id_list:
                return True
        return False

    @property
    def other_fleet_ship_ids(self):
        """第一艦隊以外に所属している艦のIDリスト"""
        res: list[int] = []
        for deck in self.deck_list[1:]:
            res.extend(deck.ship_id_list)
        return res

    def get_ship(self, id: int):
        """idから艦を取得する"""
        return next(ship for ship in self.ship_list if ship.id == id)


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
    pause_flag = False
    task_doing_flag = False
    skip_sortie: bool = True

    @classmethod
    async def do_task(cls):
        if cls.task is not None:
            cls.task_doing_flag = True
            await cls.task()
            cls.task = None
            cls.task_doing_flag = False

    @classmethod
    def set_page(cls, page: Page):
        cls.page = page

    @classmethod
    async def set_page_and_response(cls, page: Page, response: Response):
        await ResponseMemory.set_response(page, response)
        cls.set_page(page)

    @classmethod
    def set_task(cls, task: Coroutine):
        if cls.pause_flag:
            print("一時停止中のため、タスクを設定しません")
            return
        if cls.task is not None:
            print("タスクが存在するため設定しません")
            return
        cls.task = task

    @classmethod
    def set_wait_task(cls, task: Coroutine):
        if cls.pause_flag:
            print("一時停止中のため、待機タスクを設定しません")
            return
        if cls.wait_task is not None:
            print("待機タスクが存在します。以前のタスクはキャンセルして上書きします。")
            cls.wait_task.cancel()
        async def do_task_and_clear():
            await task()
            cls.wait_task = None
        cls.wait_task = asyncio.create_task(do_task_and_clear())

    @classmethod
    def cancel_wait_task(cls):
        if cls.wait_task is not None:
            cls.wait_task.cancel()
            cls.wait_task = None
            print("待機タスクをキャンセルしました")

    @classmethod
    def pause(cls):
        if cls.task_doing_flag:
            print("タスク実行中のため、一時停止できません")
            return
        if cls.page != Page.PORT and cls.page != Page.START:
            print("母港画面でないため、一時停止できません")
            return
        cls.cancel_wait_task()
        cls.task = None
        cls.pause_flag = True
        print("一時停止しました")

    @classmethod
    async def resume(cls):
        if not cls.pause_flag:
            print("一時停止中ではありません")
            return
        cls.pause_flag = False
        print(
            "再開しました。一度別画面に移動してから母港に移動すると処理が再開します。"
        )

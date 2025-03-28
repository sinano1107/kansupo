from asyncio import sleep, gather
from logging import getLogger

from address import Address
from response_receiver import ResponseReceiver
from .. import PageController, ScanTarget, Rectangle
from ..mission_result import MissionResultPageController
from ..sortie import SortiePageController
from ..supply import SupplyPageController
from ..arsenal import ArsenalPageController
from ..repair import RepairPageController
from .response import PortResponse, MissionState


class PortPageController(PageController):
    """母港画面を操作するクラス"""

    LOGGER = getLogger("uvicorn.port")

    SETTING_BUTTON_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=1143, y_start=655, width=33, height=30),
        image_path="page_controllers/port/setting_button.png",
    )

    SORTIE_BUTTON = Rectangle(x_start=240, y_start=350, width=100, height=80)
    SUPPLY_BUTTON = Rectangle(x_start=75, y_start=295, width=80, height=80)
    ARSENAL_BUTTON = Rectangle(x_start=367, y_start=505, width=80, height=80)
    REPAIR_BUTTON = Rectangle(x_start=145, y_start=505, width=80, height=80)

    def __init__(self, response: dict):
        self.RESPONSE: PortResponse = PortResponse.from_dict(response)

    async def sortie(self):
        """出撃画面へ遷移する"""
        await self.click(self.SORTIE_BUTTON)
        return await SortiePageController.sync()

    async def supply(self):
        """補給画面へ遷移する"""
        await self.click(self.SUPPLY_BUTTON)
        return await SupplyPageController.sync()

    async def arsenal(self):
        """工廠画面へ遷移する"""
        await self.click(self.ARSENAL_BUTTON)
        return await ArsenalPageController.sync()

    async def repair(self):
        """入渠画面へ遷移する"""
        await self.click(self.REPAIR_BUTTON)
        return await RepairPageController.sync(self.RESPONSE)

    async def reload(self):
        """別の画面に移ってから母港画面に戻る"""
        controller = await self.arsenal()
        return await controller.port()

    @classmethod
    async def sync(cls, response) -> "PortPageController":
        _, data = await gather(
            cls.wait_until_find(cls.SETTING_BUTTON_SCAN_TARGET),
            cls.extraction_data(response),
        )
        await sleep(1)
        return await cls.handle_expedition_returned(cls(data))

    @classmethod
    async def handle_expedition_returned(
        cls,
        controller: "PortPageController",
    ) -> "PortPageController":
        """遠征から帰投した艦隊があれば回収する"""
        for fleet in controller.RESPONSE.deck_list[1:]:
            # 遠征から帰投していなければ次の艦隊を調べる
            if fleet.mission_state != MissionState.COMPLETED:
                continue

            # 遠征から帰投している場合、回収する
            # 画面をクリックし、mission_resultとportのレスポンスが返ってくるのを待つ
            wait_mission_result_response = ResponseReceiver.expect(
                Address.MISSION_RESULT
            )
            wait_port_response = ResponseReceiver.expect(Address.PORT)
            await cls.click()
            mission_result_response, port_response = await gather(
                wait_mission_result_response(),
                wait_port_response(),
            )

            # 遠征結果画面のコントローラと同期し回収を行う
            mission_result_page_controller = await MissionResultPageController.sync(
                mission_result_response
            )
            result = await mission_result_page_controller.collect()
            cls.LOGGER.info(f"遠征:{result}")

            # 新しいportレスポンスを格納した、新しい母港画面のコントローラを生成し、返す
            return await cls.sync(port_response)

        # どの艦隊も遠征から帰投していない場合、そのまま返す
        return controller

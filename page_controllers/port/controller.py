import asyncio

from adress import Address
from response_receiver import ResponseReceiver
from .. import PageController, ScanTarget, Rectangle
from ..mission_result import MissionResultPageController
from .response import PortResponse, MissionState


class PortPageController(PageController):
    """母港画面を操作するクラス"""

    SETTING_BUTTON_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=1143, y_start=655, width=33, height=30),
        image_path="page_controllers/port/setting_button.png",
    )

    def __init__(self, response: dict):
        self.RESPONSE: PortResponse = PortResponse.from_dict(response)

    @classmethod
    async def sync(cls, response) -> "PortPageController":
        _, data = await asyncio.gather(
            cls.wait_until_find(cls.SETTING_BUTTON_SCAN_TARGET),
            cls.extraction_data(response),
        )
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
            mission_result_response, port_response = await asyncio.gather(
                wait_mission_result_response(),
                wait_port_response(),
            )

            # 遠征結果画面のコントローラと同期し回収を行う
            mission_result_page_controller = await MissionResultPageController.sync(
                mission_result_response
            )
            await mission_result_page_controller.collect()

            # 新しいportレスポンスを格納した、新しい母港画面のコントローラを生成し、返す
            return await cls.sync(port_response)

        # どの艦隊も遠征から帰投していない場合、そのまま返す
        return controller

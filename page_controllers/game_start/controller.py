from asyncio import gather

from .. import PageController, Rectangle, ScanTarget
from ..port import PortPageController
from address import Address
from response_receiver import ResponseReceiver
from ships import generate_ships


class GameStartPageController(PageController):
    """ゲームスタート画面を操作するクラス"""

    GAME_START_RECTANGLE = Rectangle(x_start=700, y_start=560, width=400, height=80)
    GAME_START_SCAN_TARGET = ScanTarget(
        rectangle=GAME_START_RECTANGLE,
        image_path="page_controllers/game_start/game_start.png",
    )

    @classmethod
    async def sync(cls) -> "GameStartPageController":
        await ResponseReceiver.expect(address=Address.OPTION_SETTING)()
        await PageController.wait_until_find(cls.GAME_START_SCAN_TARGET)
        return cls()

    async def game_start(self):
        """ゲームスタートボタンをクリックする"""
        wait_getdata_res = ResponseReceiver.expect(Address.GET_DATA)
        wait_port_res = ResponseReceiver.expect(Address.PORT)
        await self.click(target=self.GAME_START_RECTANGLE)
        get_data_res, port_res = await gather(wait_getdata_res(), wait_port_res())
        await generate_ships(get_data_res)
        return await PortPageController.sync(port_res)

from ..page_controller import PageController
from adress import Address
from response_receiver import ResponseReceiver


class GameStartPageController(PageController):
    """ゲームスタート画面を操作するクラス"""

    GAME_START_RECTANGLE = PageController.Rectangle(
        x_start=700, y_start=560, width=400, height=80
    )
    GAME_START_SCAN_TARGET = PageController.ScanTarget(
        rectangle=GAME_START_RECTANGLE,
        image_path="page_controllers/game_start/game_start.png",
    )

    @classmethod
    async def sync(cls) -> "GameStartPageController":
        await ResponseReceiver.expect(address=Address.OPTION_SETTING)()
        await PageController.wait_until_find(cls.GAME_START_SCAN_TARGET)
        return GameStartPageController()

    async def game_start(self):
        wait = ResponseReceiver.expect(Address.PORT)
        await self.click(target=self.GAME_START_RECTANGLE)
        response = await wait()

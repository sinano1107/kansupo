from asyncio import sleep
from address import Address
from page_controllers.port.controller import PortPageController
from response_receiver import ResponseReceiver
from ....home import HomePageController, Rectangle, ScanTarget


class BattleStartPageController(HomePageController):
    """海域選択画面を操作するクラス"""

    TEXT_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=199, y_start=112, width=82, height=21),
        image_path="page_controllers/sortie/battle/start/text.png",
    )

    DECIDE_BUTTON = Rectangle(x_start=900, y_start=645, width=230, height=45)
    START_BUTTON = Rectangle(x_start=815, y_start=645, width=215, height=45)

    @classmethod
    async def sync(cls) -> "BattleStartPageController":
        await cls.wait_until_find(cls.TEXT_SCAN_TARGET)
        return cls()

    def area_rectangle(self, id: int):
        """「鎮守府海域」などの海域を選択するための矩形を取得する"""
        assert id > 0, "海域番号は1以上で指定してください"
        assert id <= 7, "海域番号は7以下で指定してください"

        y_start = 665
        width = 40
        height = 20

        # 南西海域
        if id == 7:
            return Rectangle(x_start=490, y_start=y_start, width=width, height=height)

        # 鎮守府海域,南西諸島海域,北方海域
        if id < 3:
            return Rectangle(
                x_start=95 * id + 110, y_start=y_start, width=width, height=height
            )

        # 西方海域,南方海域,中部海域
        return Rectangle(x_start=95 * id + 205, y_start=640, width=width, height=height)

    def no_rectangle(self, no: int):
        """「鎮守府海域」などの海域内の番号に対応する矩形を取得する"""
        assert no > 0, "海域内番号は1以上で指定してください"

        return Rectangle(
            x_start=500 * ((no - 1) % 2) + 220,
            y_start=215 * ((no - 1) // 2) + 240,
            width=290,
            height=145,
        )

    async def battle(self, maparea_id: int, mapinfo_no: int):
        """指定された海域への出撃を開始する"""
        from .. import BattlePageController

        if maparea_id != 1:
            await self.click(self.area_rectangle(maparea_id))
            await sleep(1)
        await self.click(self.no_rectangle(mapinfo_no))
        await sleep(1)
        await self.click(self.DECIDE_BUTTON)
        await sleep(1)

        wait = ResponseReceiver.expect(address=Address.BATTLE_START)
        await self.click(self.START_BUTTON)
        response = await wait()
        return await BattlePageController.sync(response)

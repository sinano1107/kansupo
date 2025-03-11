from asyncio import sleep
from .. import ScanTarget, Rectangle
from ...home import HomePageController


class MissionPageController(HomePageController):
    """遠征画面を操作するクラス"""

    TEXT_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=180, y_start=110, width=85, height=25),
        image_path="page_controllers/sortie/mission/text.png",
    )
    DECIDE_BUTTON = Rectangle(x_start=915, y_start=645, width=230, height=50)
    START_BUTTON = Rectangle(x_start=800, y_start=645, width=240, height=45)

    @classmethod
    async def sync(cls) -> "MissionPageController":
        await cls.wait_until_find(cls.TEXT_SCAN_TARGET)
        return cls()

    def destination(self, from_the_top: int):
        """遠征先の選択領域を取得する"""
        y_start = 45 * from_the_top + 200
        return Rectangle(x_start=300, y_start=y_start, width=400, height=30)

    def fleet(self, fleet_number: int):
        x_start = 490 + 45 * fleet_number
        return Rectangle(x_start=x_start, y_start=165, width=15, height=15)

    async def start(self, from_the_top: int, fleet_number: int):
        """遠征を開始する"""
        if fleet_number < 2 or fleet_number > 4:
            raise ValueError("艦隊番号は2以上4以下で指定してください")

        await self.click(self.destination(from_the_top))
        await sleep(1)
        await self.click(self.DECIDE_BUTTON)
        await sleep(1)

        # 第三艦隊、第四艦隊の時は、遠征艦隊を選択
        if fleet_number > 2:
            await self.click(self.fleet(fleet_number=fleet_number))
            await sleep(1)

        await self.click(self.START_BUTTON)
        await sleep(3)
        await self.wait_until_find(self.PORT_BUTTON_SCAN_TARGET)

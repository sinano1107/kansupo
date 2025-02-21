from asyncio import sleep
from .. import ScanTarget, Rectangle
from ..home import HomePageController


class SupplyPageController(HomePageController):
    """補給画面を操作するクラス"""

    TEXT_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=195, y_start=113, width=82, height=20),
        image_path="page_controllers/supply/text.png",
    )

    FULL_FLEET_SUPPLY_BUTTON = Rectangle(
        x_start=1070, y_start=605, width=110, height=25
    )

    FULL_FLEET_SUPPLY_BUTTON_SCAN_TARGET = ScanTarget(
        rectangle=FULL_FLEET_SUPPLY_BUTTON,
        image_path="page_controllers/supply/full_fleet_supply_button.png",
    )

    async def supply(self, fleet_number: int = 1):
        """補給を実施する"""
        if fleet_number < 1 or fleet_number > 4:
            raise ValueError("艦隊番号は1以上4以下で指定してください")

        if fleet_number > 1:
            x_start = 45 * fleet_number + 165
            await self.click(
                Rectangle(x_start=x_start, y_start=170, width=20, height=20)
            )
            await sleep(1)

        await self.click(self.FULL_FLEET_SUPPLY_BUTTON)
        await sleep(1)
        await self.wait_until_lost(self.FULL_FLEET_SUPPLY_BUTTON_SCAN_TARGET)

    @classmethod
    async def sync(cls) -> "SupplyPageController":
        await cls.wait_until_find(cls.TEXT_SCAN_TARGET, threshold=0.88)
        return cls()

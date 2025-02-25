from logging import getLogger
from typing import TYPE_CHECKING
from asyncio import sleep

from page_controllers.pagination import Pagination
from page_controllers.port.response import NDockState
from ..home import HomePageController, ScanTarget, Rectangle

if TYPE_CHECKING:
    from ..port.response import PortResponse


class RepairPageController(HomePageController, Pagination):
    """入渠画面を操作するクラス"""

    TEXT_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=205, y_start=115, width=88, height=19),
        image_path="page_controllers/repair/text.png",
    )

    REPAIR_START_BUTTON = Rectangle(x_start=925, y_start=630, width=200, height=50)
    REPAIR_START_CONFIRM_BUTTON = Rectangle(
        x_start=690, y_start=591, width=135, height=30
    )

    def __init__(self, port_response: "PortResponse"):
        Pagination.__init__(self, contents_count=len(port_response.ship_list))
        self.LOGGER = getLogger("uvicorn.repair")
        self.port_response = port_response

    def page_button(self, index_from_left):
        x_start = 737 + 53 * index_from_left
        return Rectangle(x_start=x_start, y_start=673, width=15, height=15)

    async def click_dock(self, index: int):
        """入渠ドックをクリックする"""
        y_start = 122.5 * index + 225
        await self.click(Rectangle(x_start=280, y_start=y_start, width=200, height=25))

    async def click_ship(self, index: int):
        """艦娘リストの指定されたindexをクリックする"""
        y_start = 46 * index + 190
        await self.click(Rectangle(x_start=600, y_start=y_start, width=500, height=39))

    async def repair(self):
        """
        入渠を実施する
        入渠操作中に他のドックで入渠終了したりするとおかしくなるので、一回毎に母港ページに戻る
        """
        ship = self.port_response.ships_needing_repair[0]
        ship_index = self.port_response.ships_sorted_by_damage_ratio.index(ship)

        dock_index = None
        for index, ndock in enumerate(self.port_response.ndock_list):
            if ndock.state != NDockState.EMPTY:
                continue
            dock_index = index
            break
        if dock_index is None:
            raise ValueError("入渠可能なドックが見つかりませんでした")

        self.LOGGER.info(f"{ship}を{dock_index+1}番ドックに入渠させます")

        await self.click_dock(dock_index)
        await sleep(1)
        await self.move_page(content_index=ship_index)
        await sleep(1)
        await self.click_ship(ship_index % 10)
        await sleep(1)
        await self.click(self.REPAIR_START_BUTTON)
        await sleep(1)
        await self.click(self.REPAIR_START_CONFIRM_BUTTON)
        await sleep(1)
        return await self.port()

    @classmethod
    async def sync(cls, port_response: "PortResponse") -> "RepairPageController":
        await cls.wait_until_find(cls.TEXT_SCAN_TARGET)
        return cls(port_response=port_response)

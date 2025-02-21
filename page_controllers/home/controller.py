from abc import ABCMeta

from .. import PageController, ScanTarget, Rectangle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..port import PortPageController


class HomePageController(PageController, metaclass=ABCMeta):
    """画面左に各種画面へ遷移することのできるUIが存在するページのコントローラー"""

    PORT_BUTTON_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=90, y_start=335, width=40, height=100),
        image_path="page_controllers/home/port_button.png",
    )

    async def port(self) -> "PortPageController":
        """母港画面へ遷移する"""
        from address import Address
        from response_receiver import ResponseReceiver
        from ..port import PortPageController

        wait = ResponseReceiver.expect(Address.PORT)
        await self.click(self.PORT_BUTTON_SCAN_TARGET.RECTANGLE)
        response = await wait()
        return await PortPageController.sync(response=response)

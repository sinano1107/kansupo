import asyncio
from .. import PageController, Rectangle, ScanTarget
from .response import MissionResultResponse, ClearResult


class MissionResultPageController(PageController):
    """遠征結果画面を操作するクラス"""

    NEXT_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=1125, y_start=645, width=40, height=40),
        image_path="page_controllers/mission_result/next.png",
    )

    def __init__(self, response: dict):
        self.RESPONSE: MissionResultResponse = MissionResultResponse.from_dict(response)

    async def collect(self) -> ClearResult:
        """回収を行う"""
        await self.click()
        await asyncio.sleep(1)
        await self.click()

        return self.RESPONSE.clear_result

    @classmethod
    async def sync(cls, response) -> "MissionResultPageController":
        _, data = await asyncio.gather(
            cls.wait_until_find(cls.NEXT_SCAN_TARGET),
            cls.extraction_data(response),
        )
        return cls(data)

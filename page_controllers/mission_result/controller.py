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

    async def collect(self):
        """回収を行う"""
        clear_result = self.RESPONSE.clear_result
        if clear_result == ClearResult.FAILED:
            print("遠征:失敗")
        elif clear_result == ClearResult.SUCCESS:
            print("遠征:成功")
        elif clear_result == ClearResult.GREAT_SUCCESS:
            print("遠征:大成功")
        else:
            raise ValueError(f"不明なclear_result {clear_result}")

        await self.click()
        await asyncio.sleep(1)
        await self.click()

    @classmethod
    async def sync(cls, response) -> "MissionResultPageController":
        _, data = await asyncio.gather(
            cls.wait_until_find(cls.NEXT_SCAN_TARGET),
            cls.extraction_data(response),
        )
        return cls(data)

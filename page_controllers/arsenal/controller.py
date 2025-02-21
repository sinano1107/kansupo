from ..home import HomePageController, Rectangle, ScanTarget


class ArsenalPageController(HomePageController):
    """工廠画面を操作するクラス"""

    TEXT_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=200, y_start=113, width=135, height=19),
        image_path="page_controllers/arsenal/text.png",
    )

    @classmethod
    async def sync(cls) -> "ArsenalPageController":
        await cls.wait_until_find(cls.TEXT_SCAN_TARGET)
        return cls()

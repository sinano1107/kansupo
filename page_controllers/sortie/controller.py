from .. import PageController, ScanTarget, Rectangle


class SortiePageController(PageController):
    """出撃画面を操作するクラス"""

    TEXT_SCAN_TARGET = ScanTarget(
        rectangle=Rectangle(x_start=185, y_start=110, width=90, height=25),
        image_path="page_controllers/sortie/text.png",
    )

    BATTLE_BUTTON = Rectangle(x_start=219, y_start=264, width=245, height=202)
    MISSION_BUTTON = Rectangle(x_start=893, y_start=264, width=245, height=202)

    async def battle(self):
        """出撃海域選択画面へ遷移する"""
        from .battle.start import BattleStartPageController

        await self.click(self.BATTLE_BUTTON)
        return await BattleStartPageController.sync()

    async def mission(self):
        """遠征画面へ遷移する"""
        from .mission import MissionPageController

        await self.click(self.MISSION_BUTTON)
        return await MissionPageController.sync()

    @classmethod
    async def sync(cls) -> "SortiePageController":
        await cls.wait_until_find(cls.TEXT_SCAN_TARGET)
        return cls()

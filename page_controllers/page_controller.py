from abc import abstractmethod
from asyncio import sleep
from random import uniform
import cv2
import numpy as np
from cv2.typing import MatLike

from context import Context


class PageController:
    """各種ページコントローラの基底クラス"""

    class Rectangle:
        """矩形を表すクラス"""

        def __init__(self, x_start: float, y_start: float, width: float, height: float):
            self.X_START = x_start
            self.Y_START = y_start
            self.WIDTH = width
            self.HEIGHT = height

        @property
        def X_END(self):
            return self.X_START + self.WIDTH

        @property
        def Y_END(self):
            return self.Y_START + self.HEIGHT

        def random_point(self):
            x = uniform(self.X_START, self.X_END)
            y = uniform(self.Y_START, self.Y_END)
            return (x, y)

    class ScanTarget:
        """スキャン領域と期待する画像のURLを保存するクラス"""

        def __init__(self, rectangle: "PageController.Rectangle", image_path: str):
            self.RECTANGLE = rectangle
            self.IMAGE_PATH = image_path
            self._image: MatLike = None

        @property
        def image(self):
            if self._image is None:
                self._image = cv2.imread(self.IMAGE_PATH)
            return self._image

        def crop(self, image: MatLike):
            return image[
                self.RECTANGLE.Y_START : self.RECTANGLE.Y_END,
                self.RECTANGLE.X_START : self.RECTANGLE.X_END,
            ]

    @staticmethod
    async def scan(target: "PageController.ScanTarget"):
        """画面内の指定されたターゲットとの類似度を比較する"""
        screenshot = await Context.canvas.screenshot()
        image = np.frombuffer(screenshot, dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        # サイズは同じ前提なので、類似度は1x1の配列で返ってくる
        similarity = cv2.matchTemplate(
            target.crop(image), target.image, cv2.TM_CCOEFF_NORMED
        )[0][0]
        return similarity > 0.9

    @staticmethod
    async def wait_until_find(target: ScanTarget, delay=1, max_trial=30):
        """指定したターゲットを発見するまで待機する"""
        count = 0
        while count < max_trial:
            await sleep(delay)
            if await PageController.scan(target):
                return
            count += 1
        raise ValueError("指定回数内にターゲットが見つかりませんでした")

    async def click(
        self, target=Rectangle(x_start=0, y_start=0, width=1200, height=720)
    ):
        """指定された範囲のランダムな位置をクリックする"""
        x, y = target.random_point()
        await Context.canvas.click(position={"x": x, "y": y})

    @abstractmethod
    async def sync(self) -> "PageController":
        """実際の画面との同期を図り、同期が取れたら自身のインスタンスを返す"""
        pass

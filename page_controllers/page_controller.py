from abc import ABCMeta, abstractmethod
from asyncio import sleep
import json
from random import uniform
import cv2
import numpy as np
from cv2.typing import MatLike
from playwright.async_api import Response

from context import Context


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

    def __init__(self, rectangle: "Rectangle", image_path: str):
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


class PageController(metaclass=ABCMeta):
    """各種ページコントローラの基底クラス"""

    @staticmethod
    async def scan(target: "ScanTarget", threshold=0.9):
        """画面内の指定されたターゲットとの類似度を比較する"""
        screenshot = await Context.canvas.screenshot()
        image = np.frombuffer(screenshot, dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        cropped = target.crop(image)
        if np.std(cropped) == 0:
            # 画面が単色の場合、比較できないのでFalseを返す
            return False
        # サイズは同じ前提なので、類似度は1x1の配列で返ってくる
        simirality = cv2.matchTemplate(cropped, target.image, cv2.TM_CCOEFF_NORMED)[0][
            0
        ]
        return simirality > threshold

    @staticmethod
    async def wait_until_find(target: ScanTarget, delay=1, max_trial=30, threshold=0.9):
        """指定したターゲットを発見するまで待機する"""
        count = 0
        while count < max_trial:
            await sleep(delay)
            if await PageController.scan(target, threshold=threshold):
                await sleep(1)
                return
            count += 1
        raise ValueError("指定回数内にターゲットが見つかりませんでした")

    @staticmethod
    async def wait_until_lost(target: ScanTarget, delay=1, max_trial=30):
        """指定したターゲットが消えるまで待機する"""
        count = 0
        while count < max_trial:
            await sleep(delay)
            if not await PageController.scan(target):
                await sleep(1)
                return
            count += 1
        raise ValueError("指定回数内にターゲットが消えませんでした")

    @staticmethod
    async def click(target=Rectangle(x_start=0, y_start=0, width=1200, height=720)):
        """指定された範囲のランダムな位置をクリックする"""
        x, y = target.random_point()
        await Context.canvas.click(position={"x": x, "y": y})

    @classmethod
    async def extraction_data(cls, response: Response):
        """レスポンスからapi_dataを抽出する"""
        body = await response.body()
        json_data = json.loads(body[7:])
        if not json_data["api_result"]:
            raise ValueError("データの取得に失敗しました")
        return json_data["api_data"]

    @classmethod
    @abstractmethod
    async def sync(cls) -> "PageController":
        """実際の画面との同期を図り、同期が取れたら自身のインスタンスを返す"""
        pass

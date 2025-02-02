import cv2
import numpy as np
from playwright.async_api import Locator

from .scan_target import ScanTarget


async def scan(canvas: Locator, targets: list[ScanTarget], log=False) -> int:
    """画面内の指定されたターゲットとの類似度を比較する"""
    screenshot = await canvas.screenshot()
    image = np.frombuffer(screenshot, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    for i, target in enumerate(targets):
        rectangle = target.RECTANGLE
        cropped = image[
            rectangle.Y_RANGE[0] : rectangle.Y_RANGE[1],
            rectangle.X_RANGE[0] : rectangle.X_RANGE[1],
        ]
        # croppedとtarget.IMAGEのサイズは同じ前提なので、類似度は1x1の配列で返ってくる
        similarity = cv2.matchTemplate(cropped, cv2.imread(target.IMAGE), cv2.TM_CCOEFF_NORMED)[0][0]
        if log:
            print("{}番目のターゲットとの類似度は{}です".format(i, similarity))
        if similarity > 0.9:
            return i
    return -1
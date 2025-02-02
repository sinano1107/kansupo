import cv2
import numpy as np
from playwright.sync_api import Locator

from utils.rectangle import Rectangle


class ScanTarget:
    def __init__(self, rectangle: Rectangle, image: str):
        self.RECTANGLE = rectangle
        self.IMAGE = image


def scan(canvas: Locator, targets: list[ScanTarget], log=False) -> int:
    screenshot = canvas.screenshot()
    image = np.frombuffer(screenshot, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    for i, target in enumerate(targets):
        cropped = image[
            target.RECTANGLE.Y_RANGE[0] : target.RECTANGLE.Y_RANGE[1],
            target.RECTANGLE.X_RANGE[0] : target.RECTANGLE.X_RANGE[1],
        ]
        # croppedとtarget.IMAGEのサイズは同じ前提なので、類似度は1x1の配列で返ってくる
        similarity = cv2.matchTemplate(
            cropped, cv2.imread(target.IMAGE), cv2.TM_CCOEFF_NORMED
        )[0][0]
        if log:
            print("{}番目のターゲットとの類似度は{}です".format(i, similarity))
        if similarity > 0.9:
            return i
    return -1

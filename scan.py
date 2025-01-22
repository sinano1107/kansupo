import cv2
import numpy as np
from playwright.async_api import Locator

from rectangle import Rectangle


class ScanTarget:
    def __init__(self, rectangle: Rectangle, image: str):
        self.RECTANGLE = rectangle
        self.IMAGE = image


async def scan(canvas: Locator, target: ScanTarget):
    await canvas.screenshot(path="screenshots/use-for-scan.png")
    image = cv2.imread("screenshots/use-for-scan.png")
    cropped = image[
        target.RECTANGLE.Y_RANGE[0] : target.RECTANGLE.Y_RANGE[1],
        target.RECTANGLE.X_RANGE[0] : target.RECTANGLE.X_RANGE[1],
    ]
    return np.array_equal(cv2.imread(target.IMAGE), cropped)

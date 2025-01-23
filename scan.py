import cv2
from playwright.sync_api import Locator

from rectangle import Rectangle


class ScanTarget:
    def __init__(self, rectangle: Rectangle, image: str):
        self.RECTANGLE = rectangle
        self.IMAGE = image


def scan(canvas: Locator, target: ScanTarget):
    canvas.screenshot(path="screenshots/use-for-scan.png")
    image = cv2.imread("screenshots/use-for-scan.png")
    cropped = image[
        target.RECTANGLE.Y_RANGE[0] : target.RECTANGLE.Y_RANGE[1],
        target.RECTANGLE.X_RANGE[0] : target.RECTANGLE.X_RANGE[1],
    ]
    similarity = cv2.matchTemplate(
        cropped, cv2.imread(target.IMAGE), cv2.TM_CCOEFF_NORMED
    )
    _, max_val, _, _ = cv2.minMaxLoc(similarity)
    # print("similarity: ", max_val)
    return max_val > 0.95

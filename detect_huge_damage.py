import cv2 as cv
import numpy as np
from cv2.typing import MatLike
from playwright.sync_api import Locator


def detect_huge_damage(canvas: Locator, log=False):
    screenshot = canvas.screenshot()
    return detect_huge_damage_from_bytes(screenshot=screenshot, log=log)


def detect_huge_damage_from_bytes(screenshot: bytes, log=False):
    image = np.frombuffer(screenshot, dtype=np.uint8)
    image = cv.imdecode(image, cv.IMREAD_COLOR)
    return detect_huge_damage_core(image, log=log)


def detect_huge_damage_from_path(path: str, log=False):
    img = cv.imread(path)
    return detect_huge_damage_core(img, log=log)


def detect_huge_damage_core(img: MatLike, log=False):
    template = cv.imread("scan_targets/images/huge_damage.png")
    res: list[int] = []
    for i in range(6):
        y_start = 68 * i + 305
        cropped = img[y_start : y_start + 18, 484:519]
        similarity = cv.matchTemplate(cropped, template, cv.TM_CCOEFF_NORMED)[0][0]
        if log:
            print("similarity: ", similarity)
        if similarity > 0.9:
            res.append(i)
    return res


if __name__ == "__main__":
    paths = [
        "tests/detect_huge_damage/1.png",
        "tests/detect_huge_damage/2.png",
        "tests/detect_huge_damage/3.png",
        "tests/detect_huge_damage/4.png",
        "tests/detect_huge_damage/5.png",
        "tests/detect_huge_damage/6.png",
    ]
    for path in paths:
        print(detect_huge_damage_from_path(path, log=True))

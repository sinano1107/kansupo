import cv2 as cv
from playwright.sync_api import Locator


def detect_huge_damage(canvas: Locator):
    path = "screenshots/use-for-detect-huge-damage.png"
    canvas.screenshot(path=path)
    return detect_huge_damage_without_screenshot(path=path)


def detect_huge_damage_without_screenshot(path: str, log=False):
    img = cv.imread(path)
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
        "test/detect_huge_damage/1.png",
        "test/detect_huge_damage/2.png",
        "test/detect_huge_damage/3.png",
        "test/detect_huge_damage/4.png",
        "test/detect_huge_damage/5.png",
        "test/detect_huge_damage/6.png",
    ]
    for path in paths:
        print(detect_huge_damage_without_screenshot(path, log=True))

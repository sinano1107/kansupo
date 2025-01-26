import cv2 as cv
from playwright.sync_api import Locator


def detect_huge_damage(canvas: Locator):
    path = "screenshots/use-for-detect-huge-damage.png"
    canvas.screenshot(path=path)
    return detect_huge_damage_without_screenshot(path=path)


def detect_huge_damage_without_screenshot(path: str):
    img = cv.imread(path)
    template = cv.imread("scan_targets/images/huge_damage.png")
    res: list[int] = []
    for i in range(6):
        y_start = 68 * i + 305
        cropped = img[y_start : y_start + 18, 484:519]
        similarity = cv.matchTemplate(cropped, template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(similarity)
        # print("similarity: ", max_val)
        if max_val > 0.9:
            res.append(i)
    return res


if __name__ == "__main__":
    print(detect_huge_damage_without_screenshot("test/detect_huge_damage/1.png"))
    print(detect_huge_damage_without_screenshot("test/detect_huge_damage/2.png"))
    print(detect_huge_damage_without_screenshot("test/detect_huge_damage/3.png"))
    print(detect_huge_damage_without_screenshot("test/detect_huge_damage/4.png"))
    print(detect_huge_damage_without_screenshot("test/detect_huge_damage/5.png"))
    print(detect_huge_damage_without_screenshot("test/detect_huge_damage/6.png"))

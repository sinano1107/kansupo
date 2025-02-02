from playwright.sync_api import Locator

from utils.rectangle import Rectangle


def click(
    canvas: Locator, target: Rectangle = Rectangle(x_range=(0, 1200), y_range=(0, 720))
):
    x, y = target.random_point()
    canvas.click(position={"x": x, "y": y})

import random
from playwright.sync_api import Locator


def click(canvas: Locator, x_range: tuple[float, float], y_range: tuple[float, float]):
    x = random.uniform(x_range[0], x_range[1])
    y = random.uniform(y_range[0], y_range[1])
    canvas.click(
        position={
            "x": x,
            "y": y,
        }
    )

    print("x:{},y:{}をクリックしました".format(x, y))


if __name__ == "__main__":
    x_range = (1, 2)
    print(random.uniform(x_range[0], x_range[1]))

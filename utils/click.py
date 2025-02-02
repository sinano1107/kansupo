from utils.context import Context
from utils.rectangle import Rectangle


async def click(target=Rectangle(x_range=(0, 1200), y_range=(0, 720))):
    """指定された範囲のランダムな位置をクリックする"""
    x, y = target.random_point()
    await Context.canvas.click(position={"x": x, "y": y})
    name = target.NAME + "を" if target.NAME else ""
    print(f"{name}クリックしました {x=} {y=}")
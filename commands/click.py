import random
from commands.command import Command


class ClickCommand(Command):
    @staticmethod
    def instantiate(args):
        if len(args) != 4:
            raise Exception("クリックコマンドには4つの引数が必要です")
        
        x_range = (float(args[0]), float(args[1]))
        y_range = (float(args[2]), float(args[3]))
        
        return ClickCommand(x_range, y_range)

    def __init__(self, x_range: tuple[float, float], y_range: tuple[float, float]):
        super().__init__()
        self.X_RANGE = x_range
        self.Y_RANGE = y_range
    
    def run(self, canvas):
        x = random.uniform(self.X_RANGE[0], self.X_RANGE[1])
        y = random.uniform(self.Y_RANGE[0], self.Y_RANGE[1])
        canvas.click(
            position={
                "x": x,
                "y": y,
            }
        )

        print("x:{},y:{}をクリックしました".format(x, y))
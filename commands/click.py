from commands.command import Command
from rectangle import Rectangle
from targets import ENABLED_TARGETS


class ClickCommand(Command):
    @staticmethod
    def instantiate(args):
        if len(args) == 1:
            target = ENABLED_TARGETS.get(args[0])
            if target == None:
                raise ValueError("不明なターゲットです {}".format(args[0]))
            return ClickCommand(target=target)
        
        if len(args) == 4:
            try:
                x_range = (float(args[0]), float(args[1]))
                y_range = (float(args[2]), float(args[3]))
            except:
                raise ValueError("入力をfloatとして解釈できませんでした")
            return ClickCommand(x_range=x_range, y_range=y_range)
        
        raise ValueError("クリックコマンドには1つ、もしくは4つの引数が必要です。\n1つの場合はターゲット名を、4つの場合はxの上限下限、yの上限下限の順に入力してください。")

    def __init__(self, target = None, x_range: tuple[float, float] = None, y_range: tuple[float, float] = None):
        super().__init__()
        self.TARGET: Rectangle = None
        if target != None:
            self.TARGET = target
        elif x_range != None and y_range != None:
            self.TARGET = Rectangle(x_range, y_range)
        else:
            raise ValueError("入力が正しくありません")
    
    def run(self, canvas):
        x, y = self.TARGET.randam_point()
        canvas.click(
            position={
                "x": x,
                "y": y,
            }
        )

        print("x:{},y:{}をクリックしました".format(x, y))
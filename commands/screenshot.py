from datetime import datetime
from commands.command import Command


class ScreenShotCommand(Command):
    @staticmethod
    def instantiate(args):
        return ScreenShotCommand()
    
    def run(self, canvas):
        if canvas == None:
            print("canvasがNoneなのでスクリーンショットを撮影できません")
        else:
            canvas.screenshot(path="screenshots/{}.png".format(datetime.now()))
            print("スクリーンショットを撮影しました")
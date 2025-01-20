from datetime import datetime
from commands.command import Command


class ScreenShotCommand(Command):
    def get_name(self):
        return "screenshot"
    
    def run(self, canvas):
        if canvas == None:
            print("canvasがNoneなのでスクリーンショットを撮影できません")
        else:
            canvas.screenshot(path="screenshots/{}.png".format(datetime.now()))
            print("スクリンショットを撮影しました")
from random import random
from time import sleep
from commands.command import Command


class WaitCommand(Command):
    @staticmethod
    def instantiate(args):
        if len(args) == 0 or len(args) > 2:
            raise ValueError("waitコマンドには1もしくは2の引数が必要です。\n一つ目の引数に最低でも待機する秒数を、二つ目の引数に最大でとる余白秒数（これはランダムに決まります）を入力してください。")
        
        max_buffer_sec = None
        try:
            min_sec = int(args[0])
            if len(args) == 2:
                max_buffer_sec = int(args[1])
        except:
            raise ValueError("引数をintとして解釈できませんでした")
        return WaitCommand(min_sec=min_sec, max_buffer_sec=max_buffer_sec)
    
    def __init__(self, min_sec: int, max_buffer_sec: int = None):
        super().__init__()
        buffer_sec = random() * (max_buffer_sec if max_buffer_sec != None else 5)
        self.wait_sec = min_sec + buffer_sec
    
    def run(self, canvas = None):
        print("{}秒待ちます".format(self.wait_sec))
        sleep(self.wait_sec)
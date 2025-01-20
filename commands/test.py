from commands.command import Command


class TestCommand(Command):
    def get_name(self):
        return "test"
    
    def run(self, canvas):
        print("テスト用のコマンドです")
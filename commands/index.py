from commands.command import Command
from commands.screenshot import ScreenShotCommand
from commands.test import TestCommand


ENABLED_COMMANDS: list[Command] = [
    ScreenShotCommand(),
    TestCommand(),
]
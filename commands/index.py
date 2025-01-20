from commands.click import ClickCommand
from commands.command import Command
from commands.screenshot import ScreenShotCommand
from commands.test import TestCommand
from commands.wait import WaitCommand

ENABLED_COMMANDS: dict[str, type[Command]] = {
    "screenshot": ScreenShotCommand,
    "click": ClickCommand,
    "wait": WaitCommand,
    "test": TestCommand,
}
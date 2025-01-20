from commands.click import ClickCommand
from commands.command import Command
from commands.screenshot import ScreenShotCommand
from commands.test import TestCommand

ENABLED_COMMANDS: dict[str, type[Command]] = {
    "screenshot": ScreenShotCommand,
    "click": ClickCommand,
    "test": TestCommand,
}
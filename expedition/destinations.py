from dataclasses import dataclass
from typing import Callable
from playwright.sync_api import Locator

from click import click
from targets import EXPEDITION_DESTINATION_SELECT_5, EXPEDITION_DESTINATION_SELECT_TOP


@dataclass(frozen=True)
class ExpeditionDestination:
    name: str
    minutes: int
    select: Callable[[Locator], None]


ED_1_1 = ExpeditionDestination(
    "1-1", 15, lambda canvas: click(canvas, EXPEDITION_DESTINATION_SELECT_TOP)
)

ED_1_5 = ExpeditionDestination(
    "1-5", 1 * 60 + 30, lambda canvas: click(canvas, EXPEDITION_DESTINATION_SELECT_5)
)

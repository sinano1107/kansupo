from playwright.sync_api import Locator
from typing import TYPE_CHECKING, Callable

from expedition.expedition_1_1 import expedition_1_1

if TYPE_CHECKING:
    from expedition_manage_thread import ExpeditionManageThread


def handle_expedition(name: str) -> Callable[[Locator, "ExpeditionManageThread"], None]:
    if name == "1-1":
        return expedition_1_1
    else:
        print("{}は不明な遠征先です".format(name))

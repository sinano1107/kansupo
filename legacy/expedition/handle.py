from typing import TYPE_CHECKING
from expedition.destinations import ED_1_1, ED_1_5, ExpeditionDestination
from expedition.go_expedition import go_expedition

if TYPE_CHECKING:
    from legacy.expedition_manage_thread import ExpeditionManageThread


def handle_expedition(name: str, expedition_manage_thread: "ExpeditionManageThread"):
    destination: ExpeditionDestination = None
    if name == "1-1":
        destination = ED_1_1
    elif name == "1-5":
        destination = ED_1_5
    else:
        print("{}は不明な遠征先です".format(name))
        return
    return lambda: go_expedition(
        expedition_manage_thread,
        destination,
    )

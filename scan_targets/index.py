from rectangle import Rectangle
from scan import ScanTarget
from targets import (
    EXPEDITION_NEXT,
    GAME_START,
    GO_BACK,
    HOME_PORT,
    SORTIE_NEXT,
    SEA_AREA_SELECT,
    SETTING,
    SORTIE_SELECT,
    SORTIE_START,
    WITHDRAWAL,
)

ROOT = "scan_targets/images/"


GAME_START_SCAN_TARGET = ScanTarget(GAME_START, ROOT + "game_start.png")

SETTING_SCAN_TARGET = ScanTarget(SETTING, ROOT + "setting.png")

HOME_PORT_SCAN_TARGET = ScanTarget(HOME_PORT, ROOT + "home_port.png")

SORTIE_SELECT_SCAN_TARGET = ScanTarget(SORTIE_SELECT, ROOT + "sortie_select.png")

SEA_AREA_SELECT_SCAN_TARGET = ScanTarget(SEA_AREA_SELECT, ROOT + "sea_area_select.png")

EXPEDITION_DESTINATION_SELECT_SCAN_TARGET = ScanTarget(
    Rectangle(x_range=(180, 265), y_range=(110, 135)),
    ROOT + "expedition_destination_select.png",
)

EXPEDITION_NEXT_SCAN_TARGET = ScanTarget(EXPEDITION_NEXT, ROOT + "expedition_next.png")

# 「単縦陣」選択ボタンの「単」
TAN = ScanTarget(Rectangle(x_range=(637, 659), y_range=(266, 290)), ROOT + "tan.png")

SORTIE_NEXT_SCAN_TARGET = ScanTarget(SORTIE_NEXT, ROOT + "sortie_next.png")

GO_BACK_SCAN_TARGET = ScanTarget(GO_BACK, ROOT + "go_back.png")

WITHDRAWAL_SCAN_TARGET = ScanTarget(WITHDRAWAL, ROOT + "withdrawal.png")

# 羅針盤
COMPASS = ScanTarget(
    Rectangle(x_range=(450, 750), y_range=(210, 510)), ROOT + "compass.png"
)

EXPEDITION_RETURN_MESSAGE = ScanTarget(
    Rectangle(x_range=(855, 1075), y_range=(40, 65)),
    ROOT + "expedition_return_message.png",
)

# 夜戦選択画面
MIDNIGHT_BATTLE_SELECT_PAGE = ScanTarget(
    Rectangle(x_range=(60, 190), y_range=(45, 80)), ROOT + "midnight_battle_select_page.png"
)

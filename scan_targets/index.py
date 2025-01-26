from rectangle import Rectangle
from scan import ScanTarget
from targets import (
    GAME_START,
    GO_BACK,
    NEXT,
    SEA_AREA_SELECT,
    SETTING,
    SORTIE_SELECT,
    SORTIE_START,
    WITHDRAWAL,
)

ROOT = "scan_targets/images/"


GAME_START_SCAN_TARGET = ScanTarget(GAME_START, ROOT + "game_start.png")

SETTING_SCAN_TARGET = ScanTarget(SETTING, ROOT + "setting.png")

SORTIE_SELECT_SCAN_TARGET = ScanTarget(SORTIE_SELECT, ROOT + "sortie_select.png")

SEA_AREA_SELECT_SCAN_TARGET = ScanTarget(SEA_AREA_SELECT, ROOT + "sea_area_select.png")

SORTIE_START_SCAN_TARGET = ScanTarget(SORTIE_START, ROOT + "sortie_start.png")

# 「単縦陣」選択ボタンの「単」
TAN = ScanTarget(Rectangle(x_range=(637, 659), y_range=(266, 290)), ROOT + "tan.png")

NEXT_SCAN_TARGET = ScanTarget(NEXT, ROOT + "next.png")

GO_BACK_SCAN_TARGET = ScanTarget(GO_BACK, ROOT + "go_back.png")

WITHDRAWAL_SCAN_TARGET = ScanTarget(WITHDRAWAL, ROOT + "withdrawal.png")

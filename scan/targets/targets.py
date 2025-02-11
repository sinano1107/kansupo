from utils.rectangle import Rectangle
from ..scan_target import ScanTarget
from targets.targets import (
    DEMOLITION_BUTTON,
    GAME_START,
    HOME_PORT,
    SETTING,
    WITHDRAWAL,
)

ROOT = "scan/targets/images/"


GAME_START_SCAN_TARGET = ScanTarget(GAME_START, ROOT + "game_start.png")

SETTING_SCAN_TARGET = ScanTarget(SETTING, ROOT + "setting.png")

HOME_PORT_SCAN_TARGET = ScanTarget(HOME_PORT, ROOT + "home_port.png")

SORTIE_SELECT_PAGE_SCAN_TARGET = ScanTarget(
    Rectangle(x_range=(185, 275), y_range=(110, 135)),
    ROOT + "sortie_select_page.png",
    name="出撃選択画面",
)

SEA_AREA_SELECT_SCAN_TARGET = ScanTarget(Rectangle(x_range=(190, 650), y_range=(155, 200)), ROOT + "sea_area_select.png", name="海域選択画面")

EXPEDITION_DESTINATION_SELECT_SCAN_TARGET = ScanTarget(
    Rectangle(x_range=(180, 265), y_range=(110, 135)),
    ROOT + "expedition_destination_select.png",
    name="遠征先選択画面",
)

EXPEDITION_NEXT_SCAN_TARGET = ScanTarget(Rectangle(x_range=(1125, 1170), y_range=(643, 688)), ROOT + "expedition_next.png", name="次(遠征帰還画面)")

# 陣形選択画面
FORMATION_SELECT_SCAN_TARGET = ScanTarget(
    Rectangle(x_range=(410, 760), y_range=(600, 640)),
    ROOT + "formation_select.png",
    name="陣形選択画面",
)

SORTIE_NEXT_SCAN_TARGET = ScanTarget(Rectangle(x_range=(1110, 1150), y_range=(625, 670)), ROOT + "sortie_next.png", name="次(戦闘結果画面)")

GO_BACK_SCAN_TARGET = ScanTarget(Rectangle(x_range=(1120, 1160), y_range=(637, 682)), ROOT + "go_back.png", name="帰(戦闘結果画面)")

WITHDRAWAL_CIRCLE_SCAN_TARGET = ScanTarget(
    Rectangle(x_range=(1110, 1140), y_range=(600, 635)),
    ROOT + "withdrawal_circle.png",
    name="「退」ボタン(旗艦大破時)",
)

WITHDRAWAL_SCAN_TARGET = ScanTarget(WITHDRAWAL, ROOT + "withdrawal.png")

# 羅針盤
COMPASS = ScanTarget(
    Rectangle(x_range=(450, 750), y_range=(210, 510)), ROOT + "compass.png", name="羅針盤"
)

# 夜戦選択画面
MIDNIGHT_BATTLE_SELECT_PAGE = ScanTarget(
    Rectangle(x_range=(60, 190), y_range=(45, 80)), ROOT + "midnight_battle_select_page.png", name="夜戦選択画面"
)

# 解体ボタン
DEMOLITION_BUTTON_SCAN_TARGET = ScanTarget(
    DEMOLITION_BUTTON, ROOT + "demolition_button.png", name="解体ボタン"
)

from scan import ScanTarget
from targets import GAME_START, SEA_AREA_SELECT, SETTING, SORTIE_SELECT, SORTIE_START

ROOT = "scan_targets/images/"


GAME_START_SCAN_TARGET = ScanTarget(GAME_START, ROOT + "game_start.png")

SETTING_SCAN_TARGET = ScanTarget(SETTING, ROOT + "setting.png")

SORTIE_SELECT_SCAN_TARGET = ScanTarget(SORTIE_SELECT, ROOT + "sortie_select.png")

SEA_AREA_SELECT_SCAN_TARGET = ScanTarget(SEA_AREA_SELECT, ROOT + "sea_area_select.png")

SORTIE_START_SCAN_TARGET = ScanTarget(SORTIE_START, ROOT + "sortie_start.png")

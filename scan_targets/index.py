from scan import ScanTarget
from targets import GAME_START, SETTING

ROOT = "scan_targets/images/"


GAME_START_SCAN_TARGET = ScanTarget(GAME_START, ROOT + "game_start.png")

SETTING_SCAN_TARGET = ScanTarget(SETTING, ROOT + "setting.png")

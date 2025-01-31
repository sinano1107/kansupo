from rectangle import Rectangle

# ゲームスタートボタン
GAME_START = Rectangle(x_range=(700, 1100), y_range=(560, 640))

# 設定ボタン
SETTING = Rectangle(x_range=(1143, 1176), y_range=(655, 685))

# 母港ボタン(補給画面、改装画面などで左に表示される四角のもの)
HOME_PORT = Rectangle(x_range=(90, 130), y_range=(335, 435))

# 出撃ボタン(母港)
SORTIE = Rectangle(x_range=(240, 340), y_range=(350, 430))

# 補給ボタン(母港)
SUPPLY = Rectangle(x_range=(75, 155), y_range=(295, 375))

# 入渠ボタン(母港)
REPAIR = Rectangle(x_range=(145, 225), y_range=(505, 585))

# 入渠ドックのn番目(0~3)
def repair_dock_button(n: int):
    y_start = 122.5 * n + 225
    return Rectangle(x_range=(280, 480), y_range=(y_start, y_start + 25))

# 入渠の上からn番目の艦(0~9)
def repair_ship(n: int):
    y_start = 46 * n + 190
    return Rectangle(x_range=(600, 1100), y_range=(y_start, y_start + 39))

# 入渠開始
REPAIR_START = Rectangle(x_range=(925, 1125), y_range=(630, 680))

# 入渠開始確認
REPAIR_START_CONFIRM = Rectangle(x_range=(690, 825), y_range=(591, 621))

# 艦隊全補給
FULL_FLEET_SUPPLY = Rectangle(x_range=(1070, 1180), y_range=(605, 630))

# 出撃選択ボタン(出撃選択画面)
SORTIE_SELECT = Rectangle(x_range=(219, 464), y_range=(264, 466))

# 遠征選択ボタン（出撃選択画面）
EXPEDITION_SELECT = Rectangle(x_range=(893, 1138), y_range=(264, 466))

# 遠征先選択一番上
EXPEDITION_DESTINATION_SELECT_TOP = Rectangle(x_range=(300, 700), y_range=(245, 275))

# 遠征先選択5番目
EXPEDITION_DESTINATION_SELECT_5 = Rectangle(x_range=(300, 700), y_range=(425, 455))

# 遠征先選択決定
EXPEDITION_DESTINATION_SELECT_DECIDE = Rectangle(
    x_range=(915, 1145), y_range=(645, 695)
)

# 遠征開始ボタン
EXPEDITION_START = Rectangle(x_range=(800, 1040), y_range=(645, 690))

# 遠征帰還「次」ボタン
EXPEDITION_NEXT = Rectangle(x_range=(1125, 1170), y_range=(643, 688))

# 海域選択画面
SEA_AREA_SELECT = Rectangle(x_range=(190, 650), y_range=(155, 200))

# 海域選択左上
SEA_AREA_LEFT_TOP = Rectangle(x_range=(210, 540), y_range=(230, 390))

# 海域選択決定
SEA_AREA_SELECT_DECIDE = Rectangle(x_range=(900, 1130), y_range=(645, 690))

# 出撃開始ボタン
SORTIE_START = Rectangle(x_range=(815, 1030), y_range=(645, 690))

# 単縦陣選択ボタン
SELECT_SINGLE_LINE = Rectangle(x_range=(600, 740), y_range=(260, 295))

# 出撃時「次」ボタン
SORTIE_NEXT = Rectangle(x_range=(1110, 1150), y_range=(625, 670))

# 「帰]ボタン
GO_BACK = Rectangle(x_range=(1120, 1160), y_range=(637, 682))

# 「撤退」ボタン
WITHDRAWAL = Rectangle(x_range=(705, 815), y_range=(325, 405))

# 「進撃」ボタン
ATTACK = Rectangle(x_range=(375, 485), y_range=(325, 405))

# 「追撃せず」ボタン(夜戦選択画面)
NO_MIDNIGHT_BATTLE = Rectangle(x_range=(380, 480), y_range=(325, 405))

# 「夜戦突入」ボタン
DO_MIDNIGHT_BATTLE = Rectangle(x_range=(705, 805), y_range=(325, 405))
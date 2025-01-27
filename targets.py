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

# 艦隊全補給
FULL_FLEET_SUPPLY = Rectangle(x_range=(1070, 1180), y_range=(605, 630))

# 出撃選択ボタン(出撃選択画面)
SORTIE_SELECT = Rectangle(x_range=(219, 464), y_range=(264, 466))

# 遠征選択ボタン（出撃選択画面）
EXPEDITION_SELECT = Rectangle(x_range=(893, 1138), y_range=(264, 466))

# 遠征先選択一番上
EXPEDITION_DESTINATION_SELECT_TOP = Rectangle(x_range=(300, 700), y_range=(245, 275))

# 遠征先選択決定
EXPEDITION_DESTINATION_SELECT_DECIDE = Rectangle(
    x_range=(915, 1145), y_range=(645, 695)
)

# 遠征開始ボタン
EXPEDITION_START = Rectangle(x_range=(800, 1040), y_range=(645, 690))

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

# 「次」ボタン
NEXT = Rectangle(x_range=(1110, 1150), y_range=(625, 670))

# 「帰]ボタン
GO_BACK = Rectangle(x_range=(1120, 1160), y_range=(637, 682))

# 「撤退」ボタン
WITHDRAWAL = Rectangle(x_range=(705, 815), y_range=(325, 405))

# 「進撃」ボタン
ATTACK = Rectangle(x_range=(375, 485), y_range=(325, 405))

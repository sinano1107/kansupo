from rectangle import Rectangle

# ゲームスタートボタン
GAME_START = Rectangle(x_range=(700, 1100), y_range=(560, 640))

# 設定ボタン
SETTING = Rectangle(x_range=(1143, 1176), y_range=(655, 685))

# 出撃ボタン(母港)
SORTIE = Rectangle(x_range=(240, 340), y_range=(350, 430))

# 出撃選択ボタン(出撃選択画面)
SORTIE_SELECT = Rectangle(x_range=(219, 464), y_range=(264, 466))

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

ENABLED_TARGETS: dict[str, Rectangle] = {
    "sortie": SORTIE,
}

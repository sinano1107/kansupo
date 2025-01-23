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

ENABLED_TARGETS: dict[str, Rectangle] = {
    "sortie": SORTIE,
}

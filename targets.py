from rectangle import Rectangle

# ゲームスタートボタン
GAME_START = Rectangle(x_range=(700, 1100), y_range=(560, 640))

# 設定ボタン
SETTING = Rectangle(x_range=(1143, 1176), y_range=(655, 685))

# 出撃ボタン
SORTIE = Rectangle(x_range=(240, 340), y_range=(350, 430))

ENABLED_TARGETS: dict[str, Rectangle] = {
    "sortie": SORTIE,
}

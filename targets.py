from rectangle import Rectangle

# ゲームスタート
GAME_START = Rectangle(x_range=(700, 1100), y_range=(560, 640))

# 出撃ボタン
SORTIE = Rectangle(x_range=(240, 340), y_range=(350, 430))

ENABLED_TARGETS: dict[str, Rectangle] = {
    "sortie": SORTIE,
}
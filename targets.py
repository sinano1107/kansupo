from rectangle import Rectangle

# 出撃ボタン
SORTIE = Rectangle(x_range=(240, 340), y_range=(350, 430))

ENABLED_TARGETS: dict[str, Rectangle] = {
    "sortie": SORTIE,
}
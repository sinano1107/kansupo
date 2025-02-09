from utils.rectangle import Rectangle

# ゲームスタートボタン
GAME_START = Rectangle(x_range=(700, 1100), y_range=(560, 640), name="ゲームスタートボタン")

# 設定ボタン
SETTING = Rectangle(x_range=(1143, 1176), y_range=(655, 685), name="設定ボタン")

# 母港ボタン(補給画面、改装画面などで左に表示される四角のもの)
HOME_PORT = Rectangle(x_range=(90, 130), y_range=(335, 435), name="母港ボタン")

# 出撃ボタン(母港)
SORTIE = Rectangle(x_range=(240, 340), y_range=(350, 430), name="出撃ボタン(母港)")

# 補給ボタン(母港)
SUPPLY = Rectangle(x_range=(75, 155), y_range=(295, 375), name="補給ボタン(母港)")

# 入渠ボタン(母港)
REPAIR = Rectangle(x_range=(145, 225), y_range=(505, 585), name="入渠ボタン(母港)")

# 工廠ボタン(母港)
ARSENAL = Rectangle(x_range=(367, 447), y_range=(505, 585), name="工廠ボタン(母港)")

# 解体ボタン
DEMOLITION = Rectangle(x_range=(260, 440), y_range=(360, 420), name="解体ボタン")

# 入渠ドックのn番目(0~3)
def repair_dock_button(n: int):
    y_start = 122.5 * n + 225
    return Rectangle(x_range=(280, 480), y_range=(y_start, y_start + 25), name=f"入渠ドック{n + 1}")

# 入渠の上からn番目の艦(0~9)
def repair_ship(n: int):
    y_start = 46 * n + 190
    return Rectangle(x_range=(600, 1100), y_range=(y_start, y_start + 39), name=f"入渠の上から{n + 1}番目の艦")


# 入渠のページ選択 左から何番目か(1~5)
def repair_page_from_the_left(n: int):
    x_start = 737 + 53 * (n - 1)
    return Rectangle(
        x_range=(x_start, x_start + 15),
        y_range=(673, 688),
        name=f"入渠のページ選択 左から{n}番目",
    )


# 入渠開始
REPAIR_START = Rectangle(x_range=(925, 1125), y_range=(630, 680), name="入渠開始ボタン")

# 入渠開始確認
REPAIR_START_CONFIRM = Rectangle(x_range=(690, 825), y_range=(591, 621), name="入渠開始確認ボタン")

# 艦隊全補給
FULL_FLEET_SUPPLY = Rectangle(x_range=(1070, 1180), y_range=(605, 630), name="艦隊全補給ボタン")

# 出撃選択ボタン(出撃選択画面)
SORTIE_SELECT = Rectangle(x_range=(219, 464), y_range=(264, 466), name="出撃選択ボタン(出撃選択画面)")

# 遠征選択ボタン（出撃選択画面）
EXPEDITION_SELECT = Rectangle(x_range=(893, 1138), y_range=(264, 466), name="遠征選択ボタン（出撃選択画面）")

# 遠征先選択一番上
EXPEDITION_DESTINATION_SELECT_TOP = Rectangle(x_range=(300, 700), y_range=(245, 275), name="遠征先選択一番上")

# 遠征先選択5番目
EXPEDITION_DESTINATION_SELECT_5 = Rectangle(x_range=(300, 700), y_range=(425, 455), name="遠征先選択5番目")

# 遠征先選択決定
EXPEDITION_DESTINATION_SELECT_DECIDE = Rectangle(x_range=(915, 1145), y_range=(645, 695), name="征先選択決定ボタン")

# 遠征開始ボタン
EXPEDITION_START = Rectangle(x_range=(800, 1040), y_range=(645, 690), name="遠征開始ボタン")


# 海域選択ボタン
def sea_area(maparea_id: int, mapinfo_no: int):
    if maparea_id != 1:
        raise ValueError("maparea_idは現在1以外に対応していません")
    if mapinfo_no < 1 or mapinfo_no > 5:
        raise ValueError(
            "mapinfo_noは1以上5以下である必要があります(5以上にはまだ対応していません)"
        )

    x_start = 715 - (mapinfo_no % 2 * 505)
    y_start = mapinfo_no // 3 * 215 + 230

    return Rectangle(
        x_range=(x_start, x_start + 430),
        y_range=(y_start, y_start + 160),
        name=f"海域{maparea_id}-{mapinfo_no}",
    )

# 海域選択決定
SEA_AREA_SELECT_DECIDE = Rectangle(x_range=(900, 1130), y_range=(645, 690), name="海域選択決定")

# 出撃開始ボタン
SORTIE_START = Rectangle(x_range=(815, 1030), y_range=(645, 690), name="出撃開始ボタン")

# 単縦陣選択ボタン
SELECT_SINGLE_LINE = Rectangle(x_range=(600, 740), y_range=(260, 295), name="単縦陣選択ボタン")

# 「撤退」ボタン
WITHDRAWAL = Rectangle(x_range=(705, 815), y_range=(325, 405), name="「撤退」ボタン")

# 「進撃」ボタン
ATTACK = Rectangle(x_range=(375, 485), y_range=(325, 405), name="「進撃」ボタン")

# 「追撃せず」ボタン(夜戦選択画面)
NO_MIDNIGHT_BATTLE = Rectangle(x_range=(380, 480), y_range=(325, 405), name="「追撃せず」ボタン(夜戦選択画面)")

# 「夜戦突入」ボタン
DO_MIDNIGHT_BATTLE = Rectangle(x_range=(705, 805), y_range=(325, 405), name="「夜戦突入」ボタン")


# 解体のページ選択 左から何番目か(1~5)
def demolition_page_from_the_left(n: int):
    x_start = 432 + 53 * (n - 1)
    return Rectangle(
        x_range=(x_start, x_start + 15),
        y_range=(672, 687),
        name=f"解体のページ選択 左から{n}番目",
    )


# 解体の上からn番目の艦(0~9)
def demolition_ship(n: int):
    y_start = 46 * n + 188
    return Rectangle(
        x_range=(300, 800),
        y_range=(y_start, y_start + 39),
        name=f"解体の上から{n + 1}番目の艦",
    )


# 解体ボタン
DEMOLITION_BUTTON = Rectangle(
    x_range=(970, 1120), y_range=(635, 675), name="解体ボタン"
)

from enum import Enum


class Page(Enum):
    START = "START"
    PORT = "PORT"
    NDOCK = "NDOCK"
    # 出撃開始ページ
    SORTIE_START = "SORTIE_START"
    # 戦闘中
    BATTLE = "BATTLE"
    # 夜戦中
    MIDNIGHT_BATTLE = "MIDNIGHT_BATTLE"
    # 戦闘結果
    BATTLE_RESULT = "BATTLE_RESULT"
    # 次のセルへ移動中
    GOING_TO_NEXT_CELL = "GOING_TO_NEXT_CELL"
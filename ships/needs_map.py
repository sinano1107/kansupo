from math import inf
from ships.ship import Ship
from .ships import (
    睦月,
    如月,
    長月,
    三日月,
    吹雪,
    吹雪改,
    白雪,
    白雪改,
    深雪,
    磯波,
    綾波,
    綾波改,
    敷波,
    曙,
    潮,
    陽炎,
    不知火,
    黒潮,
    雪風,
    長良,
    五十鈴,
    暁,
    電,
    雷,
    多摩,
    多摩改,
    文月,
    時雨,
    時雨改,
    五月雨,
    北上,
    北上改,
    叢雲,
    初雪,
    川内改,
    龍田,
    白露,
    大潮,
    那珂,
    皐月,
    夕立,
    夕立改,
    初霜,
    菊月,
    霞,
    霞改,
    霰,
    満潮,
    若葉,
    神通,
    天龍,
    木曾,
    涼風,
    望月,
    子日,
    響,
    響改,
    荒潮,
    鳳翔,
    村雨,
    朧,
    初春,
    漣,
    秋雲,
    早霜,
    朝潮,
    祥鳳,
    祥鳳改,
    清霜,
    瑞穂,
    名取,
    択捉,
    松輪,
    由良,
    川内,
    加古,
    古鷹,
    長鯨,
    山風,
    球磨,
    青葉,
    千代田改,
    千代田航,
    第三〇号海防艦,
    足柄,
    摩耶,
    長門改,
    陸奥,
    高雄,
    山雲,
    鳥海,
    最上,
    浜波,
    扶桑,
    扶桑改,
    比叡,
    愛宕,
    隼鷹,
    山城,
    天霧,
    大井,
    Johnston,
    赤城,
    飛鷹,
    榛名,
)


ship_needs_map: dict[Ship, int] = {
    睦月: 1,
    如月: 1,
    長月: 1,
    三日月: 1,
    吹雪: 0,
    吹雪改: inf,
    白雪: 0,
    白雪改: inf,
    深雪: 1,
    磯波: 1,
    綾波: 0,
    綾波改: inf,
    敷波: 1,
    曙: 1,
    潮: 1,
    陽炎: 1,
    不知火: 1,
    黒潮: 1,
    雪風: inf,
    長良: 1,
    五十鈴: inf,
    暁: 1,
    電: 1,
    雷: 1,
    多摩: 0,
    多摩改: inf,
    文月: 1,
    時雨: 0,
    時雨改: inf,
    五月雨: 1,
    北上: 0,
    北上改: inf,
    叢雲: 1,
    初雪: 1,
    川内: 0,
    川内改: inf,
    龍田: 1,
    白露: 1,
    大潮: 1,
    那珂: 1,
    皐月: 1,
    夕立: 0,
    夕立改: inf,
    初霜: 1,
    菊月: 1,
    霞: 0,
    霞改: inf,
    霰: 1,
    満潮: 1,
    若葉: 1,
    神通: 1,
    天龍: 1,
    木曾: 1,
    涼風: 1,
    望月: 1,
    子日: 1,
    響: 0,
    響改: inf,
    荒潮: 1,
    鳳翔: 1,
    村雨: 1,
    朧: 1,
    初春: 1,
    漣: 1,
    秋雲: 1,
    早霜: 1,
    朝潮: 1,
    祥鳳: 0,
    祥鳳改: inf,
    清霜: 1,
    瑞穂: inf,
    名取: 1,
    択捉: inf,
    松輪: inf,
    由良: 1,
    加古: 1,
    古鷹: 1,
    長鯨: inf,
    山風: inf,
    球磨: 1,
    青葉: 1,
    千代田改: inf,
    千代田航: inf,
    第三〇号海防艦: inf,
    足柄: 1,
    摩耶: 1,
    長門改: inf,
    陸奥: 1,
    高雄: 1,
    山雲: 1,
    鳥海: 1,
    最上: 1,
    浜波: 1,
    扶桑: 0,
    扶桑改: inf,
    比叡: 1,
    愛宕: 1,
    隼鷹: 1,
    山城: 1,
    天霧: 1,
    大井: 1,
    Johnston: inf,
    赤城: inf,
    飛鷹: 1,
    榛名: 1,
}

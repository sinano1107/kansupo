from time import sleep
from playwright.sync_api import Locator
from legacy.click import click
from legacy.detect_huge_damage import detect_huge_damage
from legacy.random_sleep import random_sleep
from scan.targets.targets import (
    COMPASS,
    GO_BACK_SCAN_TARGET,
    SORTIE_NEXT_SCAN_TARGET,
    SEA_AREA_SELECT_SCAN_TARGET,
    SETTING_SCAN_TARGET,
    SORTIE_SELECT_SCAN_TARGET,
    TAN,
    WITHDRAWAL_SCAN_TARGET,
)
from targets import (
    ATTACK,
    SEA_AREA_LEFT_TOP,
    SEA_AREA_SELECT_DECIDE,
    SELECT_SINGLE_LINE,
    SORTIE,
    SORTIE_START,
)
from legacy.wait_until_find import wait_until_find, wait_until_find_any


def sortie_1_1(canvas: Locator):
    print("1-1に出撃します")

    print("出撃ボタンを押下します")
    click(canvas, SORTIE)

    print("出撃画面が出現するまで待機します")
    wait_until_find(canvas, SORTIE_SELECT_SCAN_TARGET)
    print("出撃画面が出現しました")

    random_sleep()

    print("出撃を選択します")
    click(canvas, SORTIE_SELECT_SCAN_TARGET.RECTANGLE)

    print("海域選択画面が出現するまで待機します")
    wait_until_find(canvas, SEA_AREA_SELECT_SCAN_TARGET)
    print("海域選択画面が出現しました")

    random_sleep()

    print("左上の海域を選択します")
    click(canvas, SEA_AREA_LEFT_TOP)

    random_sleep()

    print("決定します")
    click(canvas, SEA_AREA_SELECT_DECIDE)

    random_sleep()

    print("出撃開始ボタンを押下します")
    click(canvas, SORTIE_START)

    sleep(5)

    print("単縦陣選択ボタンが出現するまで待機します")
    wait_until_find(canvas, TAN)
    print("単縦陣選択ボタンが出現しました")

    random_sleep()

    print("単縦陣選択ボタンを押下します")
    click(canvas, SELECT_SINGLE_LINE)
    print("単縦陣を選択しました")

    sleep(15)

    print("戦闘終了まで待機します")
    wait_until_find(canvas, SORTIE_NEXT_SCAN_TARGET)
    print("戦闘終了しました")

    random_sleep()

    print("次へ進みます")
    click(canvas)
    print("次へ進みました")

    print("次へボタンが表示されるまで待機します")
    wait_until_find(canvas, SORTIE_NEXT_SCAN_TARGET)

    print("大破艦がいるか確認します")
    huge_damage = detect_huge_damage(canvas)
    should_withdrawal = len(huge_damage) > 0
    if should_withdrawal and 0 in huge_damage:
        print("旗艦が大破しています")
        print("この場合の処理は未記述のため、処理を終了します")
        return

    click(canvas)

    print("帰るボタンが出現(=艦娘ドロップ)、もしくは帰還ボタンが出現するまで待機します")
    res = wait_until_find_any(
        canvas,
        [GO_BACK_SCAN_TARGET, WITHDRAWAL_SCAN_TARGET],
    )
    if res == 0:
        print("帰るボタンが表示されました")
        random_sleep()
        print("クリックします")
        click(canvas)
        wait_until_find(canvas, WITHDRAWAL_SCAN_TARGET)
        random_sleep()
    elif res == 1:
        print("撤退ボタンが表示されました")
        random_sleep()
    else:
        print("不明なケースです\r処理を終了します", res)
        return

    if should_withdrawal:
        print("撤退ボタンをクリックします")
        click(canvas, WITHDRAWAL_SCAN_TARGET.RECTANGLE)

        print("母港に戻るまで待機します")
        wait_until_find(canvas, SETTING_SCAN_TARGET)
        print("母港に戻りました")
        return

    print("進撃ボタンをクリックします")
    click(canvas, ATTACK)
    print("進撃ボタンをクリックしました")

    print("羅針盤出現まで待機します")
    wait_until_find(canvas, COMPASS)
    print("羅針盤が出現しました")

    print("クリックします")
    click(canvas)
    print("クリックしました")

    sleep(5)

    print("単縦陣選択ボタンが出現するまで待機します")
    wait_until_find(canvas, TAN)
    print("単縦陣選択ボタンが出現しました")

    random_sleep()

    print("単縦陣選択ボタンを押下します")
    click(canvas, SELECT_SINGLE_LINE)
    print("単縦陣を選択しました")

    sleep(10)

    print("戦闘終了まで待機します")
    wait_until_find(canvas, SORTIE_NEXT_SCAN_TARGET)
    print("戦闘終了しました")

    random_sleep()

    print("次へ進みます")
    click(canvas)
    print("次へ進みました")

    print("次へボタンが表示されるまで待機します")
    wait_until_find(canvas, SORTIE_NEXT_SCAN_TARGET)
    print("次へボタンが表示されました")
    click(canvas)
    print("次へボタンをクリックしました")

    print("帰るボタンか設定ボタンが表示される(=母港へ帰還)まで待機します")
    res = wait_until_find_any(
        canvas,
        [GO_BACK_SCAN_TARGET, SETTING_SCAN_TARGET],
    )
    if res == 0:
        print("帰るボタンが表示されました")
        random_sleep()
        print("クリックします")
        click(canvas)
        print("母港に帰還するまで待機します")
        wait_until_find(canvas, SETTING_SCAN_TARGET)
        print("母港に帰還しました")
    elif res == 1:
        print("母港に帰還しました")
    else:
        print("不明なケースです\r処理を終了します", res)
        return

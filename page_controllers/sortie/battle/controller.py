from asyncio import sleep
from datetime import datetime
from logging import getLogger
from address import Address
from context import Context
from page_controllers.page_controller import (
    PageController,
    Response,
    ScanTarget,
    Rectangle,
)
from .response import (
    MapNextResponse,
    BattleResponse,
    MidnightBattleResponse,
    BattleResultResponse,
)


class BattlePageController(PageController):
    """戦闘画面を操作するクラス"""

    COMPASS = ScanTarget(
        rectangle=Rectangle(x_start=450, y_start=210, width=300, height=300),
        image_path="page_controllers/sortie/battle/compass.png",
    )
    FORMATION_SELECT = ScanTarget(
        rectangle=Rectangle(x_start=410, y_start=600, width=350, height=40),
        image_path="page_controllers/sortie/battle/formation_select.png",
    )
    MIDNIGHT_BATTLE_SELECT = ScanTarget(
        rectangle=Rectangle(x_start=60, y_start=45, width=130, height=35),
        image_path="page_controllers/sortie/battle/midnight_battle_select.png",
    )
    NEXT = ScanTarget(
        rectangle=Rectangle(x_start=1110, y_start=625, width=40, height=45),
        image_path="page_controllers/sortie/battle/next.png",
    )
    BACK = ScanTarget(
        rectangle=Rectangle(x_start=1120, y_start=637, width=40, height=45),
        image_path="page_controllers/sortie/battle/back.png",
    )
    BACK_2 = ScanTarget(
        rectangle=Rectangle(x_start=1107, y_start=630, width=40, height=45),
        image_path="page_controllers/sortie/battle/back.png",
    )
    WITHDRAWAL_CIRCLE = ScanTarget(
        rectangle=Rectangle(x_start=1110, y_start=600, width=30, height=35),
        image_path="page_controllers/sortie/battle/withdrawal_circle.png",
    )
    WITHDRAWAL = ScanTarget(
        rectangle=Rectangle(x_start=705, y_start=325, width=110, height=80),
        image_path="page_controllers/sortie/battle/withdrawal.png",
    )
    SELECT_SINGLE_LINE = Rectangle(x_start=600, y_start=260, width=140, height=35)
    DO_MIDNIGHT_BATTLE = Rectangle(x_start=705, y_start=325, width=100, height=80)
    NO_MIDNIGHT_BATTLE = Rectangle(x_start=380, y_start=325, width=100, height=80)
    ATTACK = Rectangle(x_start=375, y_start=325, width=110, height=80)

    def __init__(self, response: dict):
        self.logger = getLogger("uvicorn.page_controllers.sortie.battle")
        self.response: MapNextResponse = MapNextResponse.from_dict(response)

    async def battle(self, fleet_size: int):
        from response_receiver import ResponseReceiver

        wait_port_response = ResponseReceiver.expect(Address.PORT)

        while True:
            # 羅針盤が表示されるか確認する
            if self.response.rashin_flag:
                await self.wait_until_find(self.COMPASS)
                await sleep(1)
                await self.click()
                await sleep(1)
            else:
                self.logger.info("羅針盤は表示されません")

            event_id = self.response.event_id

            # イベントなし、資源獲得、渦潮、気のせいだった、の時はスキップする
            if event_id == 1 or event_id == 2 or event_id == 3 or event_id == 6:
                if self.response.next == 0:
                    self.logger.info("スキップイベントかつ行き止まりなので終了")
                    await self.wait_until_find(self.BACK_2)
                    await sleep(1)
                    await self.click()
                    return await wait_port_response()
                else:
                    self.logger.info("スキップイベントなので次のセルへ進みます")
                    await self.wait_until_going_next_cell()
                    continue

            # 戦闘、ボス戦以外の場合は対応していない
            if event_id != 4 and event_id != 5:
                self.logger.error(f"対応していないイベントが発生しました {event_id=}")
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                await Context.canvas.screenshot(
                    path=f"not_supported_event_{event_id}_{current_time}.png"
                )
                exit()

            # 陣形選択
            if fleet_size >= 4:
                await self.wait_until_find(self.FORMATION_SELECT)
                await sleep(1)
                await self.click(self.SELECT_SINGLE_LINE)

            # TODO ここからの戦闘処理を別ページコントローラに実装した方がわかりやすそう
            # 戦闘開始まで待機
            battle_response = await ResponseReceiver.expect(Address.BATTLE)()
            battle_response = await self.extraction_data(battle_response)
            battle_response: BattleResponse = BattleResponse.from_dict(battle_response)
            friend_remaining_hp_list, enemy_remaining_hp_list = self.calc_remaining_hp(
                battle_response
            )
            friend_max_hp_list = battle_response.friend_max_hp_list

            can_midnight_battle = any(hp > 0 for hp in enemy_remaining_hp_list)
            if can_midnight_battle:
                await self.wait_until_find(self.MIDNIGHT_BATTLE_SELECT, max_trial=600)

                await sleep(1)

                if event_id == 5:
                    self.logger.info("ボスマスなので夜戦を行います")
                    await self.click(self.DO_MIDNIGHT_BATTLE)

                    # 夜戦開始まで待機
                    midnight_battle_response = await ResponseReceiver.expect(
                        Address.MIDNIGHT_BATTLE
                    )(max_seconds=600)
                    midnight_battle_response = await self.extraction_data(
                        midnight_battle_response
                    )
                    midnight_battle_response: MidnightBattleResponse = (
                        MidnightBattleResponse.from_dict(midnight_battle_response)
                    )

                    hougeki = midnight_battle_response.hougeki

                    if hougeki.at_eflag_list is None:
                        self.logger.info("夜戦が発生しませんでした")
                    else:
                        total_friend_damage_list = [0] * 6

                        for i, at_e_flag in enumerate(hougeki.at_eflag_list):
                            if at_e_flag == 1:
                                for index, damage in zip(
                                    hougeki.df_list[i], hougeki.damage_list[i]
                                ):
                                    damage, is_protected = self.calc_protected_damage(
                                        damage
                                    )

                                    self.logger.debug(
                                        f"味方の{index+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                                    )
                                    total_friend_damage_list[index] += damage

                        friend_remaining_hp_list = [
                            now - damage
                            for now, damage in zip(
                                midnight_battle_response.friend_now_hp_list,
                                total_friend_damage_list,
                            )
                        ]
                        friend_max_hp_list = midnight_battle_response.friend_max_hp_list
                else:
                    self.logger.info("ボスマスではないので、夜戦を行いません")
                    await self.click(self.NO_MIDNIGHT_BATTLE)
            else:
                self.logger.info("敵を倒し切ったので夜戦を行うことができません")

            huge_damage_list = [
                remaining_hp <= max // 4
                for remaining_hp, max in zip(
                    friend_remaining_hp_list, friend_max_hp_list
                )
            ]

            # 戦闘終了画面に遷移するまで待機
            battle_result_response = await ResponseReceiver.expect(
                Address.BATTLE_RESULT
            )(max_seconds=600)
            battle_result_response = await self.extraction_data(battle_result_response)
            battle_result_response: BattleResultResponse = (
                BattleResultResponse.from_dict(battle_result_response)
            )

            await self.wait_until_find(self.NEXT)
            await sleep(2)

            await self.click()
            await sleep(1)

            await self.wait_until_find(self.NEXT)
            await sleep(1)

            await self.click()
            await sleep(1)

            if battle_result_response.get_flag[1]:
                self.logger.info(
                    f"艦娘を取得しました: {battle_result_response.get_ship.name}"
                )
                await self.wait_until_find(self.BACK)
                await sleep(1)
                await self.click()

            if self.response.next == 0:
                self.logger.info("行き止まりなので終了")
                return await wait_port_response()

            if huge_damage_list[0]:
                self.logger.info("旗艦が大破したので撤退します")
                await self.wait_until_find(self.WITHDRAWAL_CIRCLE)
                await sleep(1)
                await self.click()
                return await wait_port_response()

            await self.wait_until_find(self.WITHDRAWAL)
            await sleep(1)

            if any(huge_damage_list):
                self.logger.info("大破艦がいるので撤退します")
                await self.click(self.WITHDRAWAL.RECTANGLE)
                return await wait_port_response()

            await self.click(self.ATTACK)

            await self.wait_until_going_next_cell()

    async def wait_until_going_next_cell(self):
        """次のセルへ向かうレスポンスが帰ってくるまで待機します"""
        from response_receiver import ResponseReceiver

        response = await ResponseReceiver.expect(Address.MAP_NEXT)()
        data = await self.extraction_data(response)
        self.response = MapNextResponse.from_dict(data)

    def calc_protected_damage(self, damage: int):
        """庇った場合はdamage+0.1になるのでそれを処理する"""
        damage, mod = divmod(damage, 1)
        is_protected = mod != 0
        return damage, is_protected

    def calc_remaining_hp(self, response: BattleResponse):
        """
        味方・敵 艦隊の残りHPを計算する
        """
        total_friend_damage_list = [0] * 6
        total_enemy_damage_list = [0] * 6

        if response.stage_flag[2]:
            self.logger.debug("<航空攻撃>")
            for i, damage in enumerate(response.kouku.stage3.fdam):
                damage, is_protected = self.calc_protected_damage(damage)
                self.logger.debug(
                    f"味方の{i+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                )
                total_friend_damage_list[i] += damage

            for i, damage in enumerate(response.kouku.stage3.edam):
                damage, is_protected = self.calc_protected_damage(damage)
                self.logger.debug(
                    f"敵の{i+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                )
                total_enemy_damage_list[i] += damage

        if response.opening_taisen_flag:
            # TODO 先制対潜のダメージを計算する
            self.logger.error("🚨先制対潜のダメージ計算は実装されていないです")
        else:
            self.logger.debug("<先制対潜は発生しませんでした>")

        if response.opening_flag:
            # TODO 先制雷撃のダメージを計算する
            self.logger.error("🚨先制雷撃のダメージ計算は実装されていないです")
        else:
            self.logger.debug("<先制雷撃は発生しませんでした>")

        # 砲撃戦の情報を取得する
        for i in range(3):
            flag = response.hourai_flag[i]
            if not flag:
                break

            self.logger.debug("<砲撃戦" + str(i + 1) + "巡目>")

            hougeki_data: BattleResponse.Hougeki = getattr(response, f"hougeki{i+1}")

            for i, at_eflag in enumerate(hougeki_data.at_eflag_list):
                for index, damage in zip(
                    hougeki_data.df_list[i], hougeki_data.damage_list[i]
                ):
                    damage, is_protected = self.calc_protected_damage(damage)

                    # ダメージを記録
                    if at_eflag == 1:
                        self.logger.debug(
                            f"味方の{index + 1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                        )
                        total_friend_damage_list[index] += damage
                    else:
                        self.logger.debug(
                            f"敵の{index + 1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                        )
                        total_enemy_damage_list[index] += damage

        # 雷撃戦の情報を取得する
        if response.hourai_flag[3]:
            raigeki = response.raigeki

            for i, damage in enumerate(raigeki.fdam[:6]):
                damage, is_protected = self.calc_protected_damage(damage)
                self.logger.debug(
                    f"味方の{i+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                )
                total_friend_damage_list[i] += damage

            for i, damage in enumerate(raigeki.edam[:6]):
                damage, is_protected = self.calc_protected_damage(damage)
                self.logger.debug(
                    f"敵の{i+1}隻目に{damage}ダメージ{'(旗艦を庇った)' if is_protected else ''}"
                )
                total_enemy_damage_list[i] += damage
        else:
            self.logger.debug("<雷撃戦は発生しませんでした>")

        friend_remaining_hp_list = [
            now - damage
            for now, damage in zip(
                response.friend_now_hp_list, total_friend_damage_list
            )
        ]
        enemy_remaining_hp_list = [
            now - damage
            for now, damage in zip(response.enemy_now_hp_list, total_enemy_damage_list)
        ]

        self.logger.debug("<トータルダメージ>")
        self.logger.debug(f"味方の被ダメージ合計: {total_friend_damage_list}")
        self.logger.debug(f"敵の被ダメージ合計: {total_enemy_damage_list}")
        self.logger.debug("<残りHP>")
        self.logger.debug(f"味方の残りHP: {friend_remaining_hp_list}")
        self.logger.debug(f"敵の残りHP: {enemy_remaining_hp_list}")

        return (friend_remaining_hp_list, enemy_remaining_hp_list)

    @classmethod
    async def sync(cls, response: Response) -> "BattlePageController":
        data = await cls.extraction_data(response)
        return BattlePageController(data)

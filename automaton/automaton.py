from math import inf
from asyncio import sleep
from logging import getLogger
from page_controllers.port import PortPageController


fleet_number_to_from_the_top = {2: 5, 3: 2}
map_area = (2, 2)


class Automaton:
    """自動で艦これを操作するクラス"""

    def __init__(self, port_page_controller: PortPageController):
        self.LOGGER = getLogger("uvicorn.automaton")
        self.port_page_controller = port_page_controller

    async def supply(self, fleet_number: int):
        supply_page_controller = await self.port_page_controller.supply()
        await supply_page_controller.supply(fleet_number=fleet_number)
        self.port_page_controller = await supply_page_controller.port()

    async def run(self):
        while True:
            response = self.port_page_controller.RESPONSE

            # 未出撃の遠征艦隊があれば遠征させる
            waiting_mission_deck = response.waiting_mission_deck
            if waiting_mission_deck:
                fleet_number = waiting_mission_deck.id

                # 補給の必要があれば補給を行う
                if response.is_supply_needed(fleet_number=fleet_number):
                    await self.supply(fleet_number=fleet_number)

                sortie_page_controller = await self.port_page_controller.sortie()
                mission_page_controller = await sortie_page_controller.mission()
                await mission_page_controller.start(
                    from_the_top=fleet_number_to_from_the_top[fleet_number],
                    fleet_number=fleet_number,
                )
                self.port_page_controller = await mission_page_controller.port()
                continue

            # 入渠が必要かつ入渠可能であれば入渠させる
            if response.can_repair and response.is_repair_needed:
                repair_page_controller = await self.port_page_controller.repair()
                self.port_page_controller = await repair_page_controller.repair()
                continue

            min_cond = response.min_cond(fleet_number=1)

            # 出撃可能であれば出撃する
            if not response.is_fleet_repair_needed(fleet_number=1) and min_cond >= 49:
                # 必要であれば補給を実施
                if response.is_supply_needed(fleet_number=1):
                    await self.supply(fleet_number=1)

                sortie_page_controller = await self.port_page_controller.sortie()
                battle_start_page_controller = await sortie_page_controller.battle()
                battle_page_controller = await battle_start_page_controller.battle(
                    maparea_id=map_area[0], mapinfo_no=map_area[1]
                )
                port_response = await battle_page_controller.battle(
                    fleet_size=self.port_page_controller.RESPONSE.deck_list[0].size
                )
                self.port_page_controller = await PortPageController.sync(
                    response=port_response
                )
                continue

            # 遠征/入渠/cond値の回復終了まで待つ
            seconds_until_mission_end = response.seconds_until_mission_end
            seconds_until_repair_end = response.seconds_until_repair_end
            seconds_until_cond_recovery = (49 - min_cond) * 60
            seconds_list = [
                (
                    seconds_until_mission_end
                    if seconds_until_mission_end is not None
                    else inf
                ),
                (
                    seconds_until_repair_end
                    if seconds_until_repair_end is not None
                    else inf
                ),
                (
                    seconds_until_cond_recovery
                    if seconds_until_cond_recovery > 0
                    else inf
                ),
            ]

            seconds = min(seconds_list)
            int_seconds = int(seconds)
            min_index = seconds_list.index(seconds)

            if min_index == 0:
                self.LOGGER.info(f"遠征終了まで{int_seconds}秒待機します")
            elif min_index == 1:
                self.LOGGER.info(f"入渠終了まで{int_seconds}秒待機します")
            elif min_index == 2:
                self.LOGGER.info(f"cond値回復まで{int_seconds}秒待機します")
            else:
                self.LOGGER.warning(f"不明の理由で{int_seconds}秒待機します")

            assert seconds >= 0, f"待ち秒数が負になりました {seconds=}"

            await sleep(seconds)
            self.port_page_controller = await self.port_page_controller.reload()

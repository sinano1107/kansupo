from math import inf
from asyncio import sleep
from logging import getLogger
from page_controllers.port import PortPageController


fleet_number_to_from_the_top = {2: 5, 3: 2}


class Automaton:
    """自動で艦これを操作するクラス"""

    def __init__(self, port_page_controller: PortPageController):
        self.LOGGER = getLogger("uvicorn.automaton")
        self.port_page_controller = port_page_controller

    async def run(self):
        while True:
            response = self.port_page_controller.RESPONSE

            # 未出撃の遠征艦隊があれば遠征させる
            waiting_mission_deck = response.waiting_mission_deck
            if waiting_mission_deck:
                fleet_number = waiting_mission_deck.id

                # 補給の必要があれば補給を行う
                if response.is_supply_needed(fleet_number=fleet_number):
                    supply_page_controller = await self.port_page_controller.supply()
                    await supply_page_controller.supply(fleet_number=fleet_number)
                    self.port_page_controller = await supply_page_controller.port()

                sortie_page_controller = await self.port_page_controller.sortie()
                mission_page_controller = await sortie_page_controller.mission()
                await mission_page_controller.start(
                    from_the_top=fleet_number_to_from_the_top[fleet_number],
                    fleet_number=fleet_number,
                )
                self.port_page_controller = await mission_page_controller.port()

            # 入渠が必要かつ入渠可能であれば入渠させる
            elif response.can_repair and response.is_repair_needed:
                repair_page_controller = await self.port_page_controller.repair()
                self.port_page_controller = await repair_page_controller.repair()

            else:
                # 遠征/入渠終了まで待つ
                seconds_until_mission_end = response.seconds_until_mission_end
                seconds_until_repair_end = (
                    response.seconds_until_repair_end
                    if response.is_repair_needed
                    else None
                )
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
                ]

                seconds = min(seconds_list)
                int_seconds = int(seconds)
                min_index = seconds_list.index(seconds)

                if min_index == 0:
                    self.LOGGER.info(f"遠征終了まで{int_seconds}秒待機します")
                elif min_index == 1:
                    self.LOGGER.info(f"入渠終了まで{int_seconds}秒待機します")
                else:
                    self.LOGGER.warn(f"不明の理由で{int_seconds}秒待機します")

                await sleep(seconds)
                self.port_page_controller = await self.port_page_controller.reload()

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
            else:
                # 遠征終了まで待つ
                seconds = response.seconds_until_mission_end

                self.LOGGER.info(f"遠征終了まで{int(seconds)}秒待機します")
                await sleep(seconds)
                self.port_page_controller = await self.port_page_controller.reload()

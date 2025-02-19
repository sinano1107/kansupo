import asyncio
from datetime import datetime, timedelta

from scan.targets.targets import HOME_PORT_SCAN_TARGET
from targets.targets import ARSENAL, HOME_PORT
from utils.click import click
from utils.context import Context
from utils.random_sleep import random_sleep
from utils.wait_until_find import wait_until_find


def wait_reload(reload_period: int):
    async def _():
        print(
            f"{datetime.now() + timedelta(seconds=reload_period)}まで待ってからリロードを行います"
        )
        await asyncio.sleep(reload_period)

        async def _():
            await random_sleep()
            await click(ARSENAL)
            await random_sleep()
            await wait_until_find(HOME_PORT_SCAN_TARGET)
            await random_sleep()
            await click(HOME_PORT)

        await Context.set_task(_)

    Context.set_wait_task(_)

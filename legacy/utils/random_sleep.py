import asyncio
from random import random


async def random_sleep(base: float = 1, buffer: float = 1):
    """ランダムな秒数待つ"""
    await asyncio.sleep(base + random() * buffer)
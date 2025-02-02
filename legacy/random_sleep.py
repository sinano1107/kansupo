from random import random
from time import sleep


def random_sleep(base: int = 1, buffer: int = 1):
    sleep(base + random() * buffer)
